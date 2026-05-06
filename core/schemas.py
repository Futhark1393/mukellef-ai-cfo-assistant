# AI Traceability: Skills Agent designed these Pydantic models to enforce
# strict data validation for invoice line items and multi-page invoice records.
# Separating schemas from business logic keeps the codebase modular and
# ready for production-grade input validation.

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=128)
    tenant_slug: str = Field(min_length=2, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(default="owner", max_length=32)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LineItem(BaseModel):
    """A single line item extracted from an invoice table."""

    line_no: int = Field(..., ge=1, description="Sequential line number starting from 1")
    description: str = Field(..., min_length=1, description="Product or service description")
    quantity: float = Field(..., gt=0, description="Quantity ordered")
    unit: str = Field(default="pcs", description="Unit of measure (pcs, kg, hours, etc.)")
    unit_price: float = Field(..., ge=0, description="Price per unit before VAT")
    vat_rate: float = Field(default=20.0, ge=0, le=100, description="VAT percentage (e.g. 20)")
    vat_amount: float = Field(..., ge=0, description="Computed VAT for this line")
    line_total: float = Field(..., ge=0, description="Total including VAT for this line")


class InvoiceDetail(BaseModel):
    """Full invoice record including header fields and line items."""

    invoice_id: str
    vendor_name: str
    date: str = Field(..., description="Invoice date in ISO 8601 format (YYYY-MM-DD)")
    currency: str = Field(default="TRY")
    category: str
    description: str
    status: str = Field(default="pending", description="processing status: pending | processed")
    page_count: int = Field(default=1, ge=1, description="Number of pages in the source PDF")
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: float = Field(..., ge=0, description="Sum of line totals before VAT")
    total_vat: float = Field(..., ge=0, description="Total VAT amount")
    total_amount: float = Field(..., ge=0, description="Grand total including VAT")


class InvoiceSummary(BaseModel):
    """Lightweight invoice summary for list views (no line items)."""

    invoice_id: str
    vendor_name: str
    date: str
    total_amount: float
    category: str
    status: str
    page_count: int = 1
    line_item_count: int = 0
