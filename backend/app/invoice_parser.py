from __future__ import annotations

import json
from typing import Any

from . import config
from .schemas import InvoiceExtract, LineItem


class InvoiceParserError(RuntimeError):
    """Raised when Extend cannot produce invoice data for the booking flow."""


_client: Any | None = None
_extractor_override_config: dict[str, Any] | None = None


def _get_client() -> Any:
    global _client
    if _client is None:
        if not config.EXTEND_API_KEY:
            raise InvoiceParserError(
                "EXTEND_API_KEY is not set. Copy backend/.env.example to backend/.env and fill it in."
            )
        try:
            from extend_ai import Extend
        except ImportError as e:
            raise InvoiceParserError(
                "Extend SDK is not installed. Run `pip install -r backend/requirements.txt`."
            ) from e
        _client = Extend(token=config.EXTEND_API_KEY)
    return _client


def _load_extractor_override_config() -> dict[str, Any]:
    global _extractor_override_config
    if _extractor_override_config is None:
        try:
            with config.EXTEND_EXTRACTOR_CONFIG_PATH.open("r", encoding="utf-8") as f:
                raw_config = json.load(f)["config"]
        except (OSError, KeyError, json.JSONDecodeError) as e:
            raise InvoiceParserError(
                "Extend extractor config could not be loaded from backend/extend_invoice_extractor_config.json."
            ) from e
        _extractor_override_config = _to_sdk_override_config(raw_config)
    return _extractor_override_config


def _to_sdk_override_config(raw_config: dict[str, Any]) -> dict[str, Any]:
    sdk_config: dict[str, Any] = {
        "schema": raw_config["schema"],
    }

    if "baseProcessor" in raw_config:
        sdk_config["base_processor"] = raw_config["baseProcessor"]
    if "baseVersion" in raw_config:
        sdk_config["base_version"] = raw_config["baseVersion"]
    if "extractionRules" in raw_config:
        sdk_config["extraction_rules"] = raw_config["extractionRules"]
    if "advancedOptions" in raw_config:
        sdk_config["advanced_options"] = _to_sdk_advanced_options(raw_config["advancedOptions"])

    return sdk_config


def _to_sdk_advanced_options(raw_options: dict[str, Any]) -> dict[str, Any]:
    sdk_options: dict[str, Any] = {}
    key_map = {
        "modelReasoningInsightsEnabled": "model_reasoning_insights_enabled",
        "advancedMultimodalEnabled": "advanced_multimodal_enabled",
        "citationsEnabled": "citations_enabled",
        "arrayCitationStrategy": "array_citation_strategy",
        "arrayStrategy": "array_strategy",
        "chunkingOptions": "chunking_options",
        "excelSheetRanges": "excel_sheet_ranges",
        "excelSheetSelectionStrategy": "excel_sheet_selection_strategy",
        "pageRanges": "page_ranges",
        "reviewAgent": "review_agent",
    }
    for raw_key, sdk_key in key_map.items():
        if raw_key in raw_options:
            sdk_options[sdk_key] = raw_options[raw_key]
    return sdk_options


def extract_invoice(pdf_bytes: bytes, filename: str) -> InvoiceExtract:
    if not config.EXTEND_EXTRACTOR_ID:
        raise InvoiceParserError(
            "EXTEND_EXTRACTOR_ID is not set. Add your Extend extractor ID to backend/.env."
        )

    client = _get_client()
    safe_filename = filename or "invoice.pdf"

    try:
        uploaded_file = client.files.upload(
            file=(safe_filename, pdf_bytes, "application/pdf"),
        )
        extract_run = client.extract_runs.create_and_poll(
            file={"id": uploaded_file.id},
            extractor={
                "id": config.EXTEND_EXTRACTOR_ID,
                "override_config": _load_extractor_override_config(),
            },
        )
        status = getattr(extract_run, "status", None)
        status_value = getattr(status, "value", status)
        print("Extend extraction status:", status)
        print("Extend extraction status value:", status_value)
        if status_value != "PROCESSED":
            raise InvoiceParserError("Invoice extraction failed before booking suggestion.")

        output = getattr(extract_run, "output", None)
        value = _get(output, "value")
        print("Extend extraction output value:", value)
        if value is None:
            raise InvoiceParserError("Invoice extraction failed before booking suggestion.")
        return normalize_extend_invoice(value)
    except InvoiceParserError:
        raise
    except Exception as e:
        raise InvoiceParserError("Invoice extraction failed before booking suggestion.") from e


def normalize_extend_invoice(value: Any) -> InvoiceExtract:
    data = _to_mapping(value)

    vendor_name = _required_str(data, "vendor_name")
    invoice_number = _required_str(data, "invoice_number")
    invoice_date = _required_str(data, "invoice_date")

    amount_net = _required_amount(_get(data, "subtotal_amount"), "subtotal_amount.amount")
    amount_gross = _required_amount(_get(data, "total_amount"), "total_amount.amount")
    tax_amount = _required_amount(_get(data, "tax_amount"), "tax_amount.amount")
    if amount_net == 0:
        raise InvoiceParserError("subtotal_amount.amount must be non-zero to compute VAT rate.")
    vat_rate = round((tax_amount / amount_net) * 100, 2)

    return InvoiceExtract(
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        vendor_name=vendor_name,
        line_items=_normalize_line_items(_get(data, "line_items")),
        amount_net=amount_net,
        amount_gross=amount_gross,
        vat_rate=vat_rate,
    )


def _normalize_line_items(value: Any) -> list[LineItem]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise InvoiceParserError("line_items must be an array.")

    items: list[LineItem] = []
    for raw_item in value:
        item = _to_mapping(raw_item)
        items.append(
            LineItem(
                description=_optional_str(_get(item, "description")),
                quantity=_quantity_to_str(_get(item, "quantity")),
                unit_price_net=_optional_amount(_get(item, "unit_price")),
                amount_net=_optional_amount(_get(item, "amount")),
            )
        )
    return items


def _to_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    raise InvoiceParserError("Extend extraction output must be an object.")


def _get(value: Any, key: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


def _required_str(data: dict[str, Any], key: str) -> str:
    value = _optional_str(_get(data, key))
    if not value:
        raise InvoiceParserError(f"{key} is missing from Extend extraction output.")
    return value


def _optional_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _quantity_to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _required_amount(value: Any, field_name: str) -> float:
    amount = _optional_amount(value)
    if amount is None:
        raise InvoiceParserError(f"{field_name} is missing from Extend extraction output.")
    return amount


def _optional_amount(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    amount = _get(value, "amount")
    if amount is None:
        return None
    if isinstance(amount, int | float):
        return float(amount)
    if isinstance(amount, str):
        stripped = amount.strip().replace(" ", "")
        if "," in stripped and "." not in stripped:
            stripped = stripped.replace(",", ".")
        try:
            return float(stripped)
        except ValueError:
            return None
    return None
