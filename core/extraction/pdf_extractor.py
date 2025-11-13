"""
Text Extraction Module

PDF ve DOCX dosyalarından metin çıkarma.
"""
from pathlib import Path
import sys


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    PDF dosyasından metin çıkarır.
    
    Args:
        pdf_path: PDF dosyasının yolu
    
    Returns:
        Çıkarılmış metin (string)
    
    Raises:
        FileNotFoundError: PDF dosyası bulunamadı
        RuntimeError: PDF okunamadı
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")
    
    # Önce pdfplumber'ı dene (daha iyi)
    try:
        import pdfplumber  # type: ignore
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip()
    
    except ImportError:
        # pdfplumber yoksa PyPDF2'yi dene
        try:
            import PyPDF2  # type: ignore
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
            return text.strip()
        
        except ImportError:
            # Her ikisi de yoksa
            raise RuntimeError(
                "PDF okuma için gerekli paketler yüklü değil.\n"
                "Şu komutu çalıştırın: pip install pdfplumber\n"
                "veya: pip install PyPDF2"
            )
        except Exception as e:
            raise RuntimeError(f"PDF okuma hatası (PyPDF2): {e}")
    
    except Exception as e:
        raise RuntimeError(f"PDF okuma hatası (pdfplumber): {e}")


def extract_text_from_docx(docx_path: str | Path) -> str:
    """
    DOCX dosyasından metin çıkarır.
    
    Args:
        docx_path: DOCX dosyasının yolu
    
    Returns:
        Çıkarılmış metin (string)
    """
    docx_path = Path(docx_path)
    
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX dosyası bulunamadı: {docx_path}")
    
    try:
        from docx import Document  # type: ignore
        doc = Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    
    except ImportError:
        raise RuntimeError(
            "DOCX okuma için python-docx paketi gerekli.\n"
            "Şu komutu çalıştırın: pip install python-docx"
        )
    except Exception as e:
        raise RuntimeError(f"DOCX okuma hatası: {e}")


def extract_text(file_path: str | Path) -> str:
    """
    Dosya tipine göre otomatik olarak metin çıkarır.
    PDF, DOCX desteklenir.
    
    Args:
        file_path: Dosya yolu
    
    Returns:
        Çıkarılmış metin
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return extract_text_from_pdf(file_path)
    elif suffix == '.docx':
        return extract_text_from_docx(file_path)
    elif suffix == '.txt':
        return file_path.read_text(encoding='utf-8')
    else:
        raise ValueError(
            f"Desteklenmeyen dosya formatı: {suffix}\n"
            "Desteklenen formatlar: .pdf, .docx, .txt"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python pdf_extractor.py <dosya_yolu>")
        print("Örnek: python pdf_extractor.py rapor.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        print(f" Dosya okunuyor: {file_path}")
        text = extract_text(file_path)
        
        print(f" Metin çıkarıldı!")
        print(f"   Uzunluk: {len(text)} karakter")
        print(f"   Satır sayısı: {len(text.splitlines())}")
        print()
        print("=" * 70)
        print("ÇIKARILAN METİN (İlk 500 karakter):")
        print("=" * 70)
        print(text[:500])
        if len(text) > 500:
            print("...")
        
        # Çıktıyı dosyaya kaydet
        output_file = Path(file_path).with_suffix('.txt')
        output_file.write_text(text, encoding='utf-8')
        print()
        print(f" Tam metin kaydedildi: {output_file}")
        
    except Exception as e:
        print(f" Hata: {e}")
        sys.exit(1)

