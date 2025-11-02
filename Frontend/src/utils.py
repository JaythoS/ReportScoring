import base64

def pdf_to_html_embed(file_bytes: bytes, height: int = 700) -> str:
    """
    Eski yöntem (artık kullanılmıyor ama yedek dursun).
    Chrome bazı sürümlerde base64 PDF'leri engellediği için
    artık pdf.js viewer kullanılıyor.
    """
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    return f"""
    <embed
      src="data:application/pdf;base64,{b64}#zoom=page-fit"
      type="application/pdf"
      width="100%"
      height="{height}"
      style="border:1px solid #e5e7eb;border-radius:12px;"
    />
    """
