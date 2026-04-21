import re
import uuid

class MarkdownLegalChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Regex patterns for Vietnamese legal structure
        self.patterns = {
            'article': r'(\n\*\*Điều \d+[:\.]\*\*|\nĐiều \d+[:\.] )',
            'chapter': r'(\n#+ Chương [IVXLCDM\d]+[:\.]?.*|\n\*\*Chương [IVXLCDM\d]+[:\.]?.*\*\*)'
        }

    def chunk_document(self, doc_metadata, content_md):
        """
        Splits a legal document into logical chunks with hierarchical context.
        doc_metadata: dict containing title, link, doc_type, etc.
        """
        title = doc_metadata.get('title', 'Văn bản không tiêu đề')
        doc_id = doc_metadata.get('id')
        
        # 0. Clean legal noise (Signatures, Receivers, etc.)
        content = self._clean_noise(content_md)
        
        # Pre-process: Ensure stable newlines for splitting
        content = "\n" + content
        
        # 1. Split by Chapter first (if exists)
        chapters = self._split_by_hierarchy(content, 'chapter')
        
        all_chunks = []
        
        for chapter_text in chapters:
            chapter_name = self._extract_header(chapter_text, 'Chương') or ""
            
            # 2. Split Chapter into Articles
            articles = self._split_by_hierarchy(chapter_text, 'article')
            
            for article_text in articles:
                article_name = self._extract_header(article_text, 'Điều') or "Nội dung"
                
                # Construct Context Breadcrumb
                breadcrumb = f"[{title}]"
                if chapter_name: breadcrumb += f" > {chapter_name}"
                breadcrumb += f" > {article_name}"
                
                # 3. Final Splitting by Size if article is too long
                clean_article_text = article_text.strip()
                if not clean_article_text: continue

                # Recursive split by Khoản (Clause) if needed
                sub_chunks = self._recursive_split(clean_article_text, self.chunk_size)
                
                for sc in sub_chunks:
                    # Generate deterministic UUID based on content
                    chunk_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{breadcrumb}\n{sc}"))
                    chunk_payload = {
                        "id": chunk_id,
                        "doc_id": doc_id,
                        "content": f"{breadcrumb}\n{sc}",
                        "metadata": {
                            **doc_metadata,
                            "breadcrumb": breadcrumb,
                            "chunk_len": len(sc)
                        }
                    }
                    all_chunks.append(chunk_payload)
                    
        return all_chunks

    def _split_by_hierarchy(self, text, level):
        pattern = self.patterns.get(level)
        if not pattern: return [text]
        
        parts = re.split(pattern, text)
        if len(parts) <= 1: return [text]
        
        # First part is text before any match
        result = [parts[0]]
        for i in range(1, len(parts), 2):
            # Combine the matched header with following content
            result.append(parts[i] + parts[i+1])
        return result

    def _extract_header(self, text, keyword):
        # Be strict: Article must be followed by digits, Chapter by Roman/Digits
        target = text.strip()[:100] # Only look at the beginning
        
        if keyword.lower() == 'điều':
            # Match "Điều 1" or "Điều 12" strictly
            match = re.search(r'Điều (\d+)', target, re.IGNORECASE)
        elif keyword.lower() == 'chương':
            # Match "Chương I" or "Chương 1"
            match = re.search(r'Chương ([IVXLCDM\d]+)', target, re.IGNORECASE)
        else:
            match = re.search(fr'({keyword} [IVXLCDM\d]+)', target, re.IGNORECASE)
            
        return match.group(0).strip('*: ') if match else None

    def _clean_noise(self, text):
        # 1. Truncate at "Nơi nhận" (the end of law body)
        noise_markers = [r'\n-?\s*Nơi nhận:', r'\nNƠI NHẬN:']
        for marker in noise_markers:
            parts = re.split(marker, text, flags=re.IGNORECASE)
            if len(parts) > 1:
                text = parts[0]
        
        # 2. Patterns to remove entirely
        signature_patterns = [
            r'TM\.\s+UBND.*',
            r'TM\.\s+ỦY BAN.*',
            r'KT\.\s+CHỦ TỊCH.*',
            r'PHÓ CHỦ TỊCH.*',
            r'\(Đã ký\)',
            r'\(Ký tên\)',
            r'\\?_{5,}',       # Lines like \_______ or _____
            r'\*{5,}',         # Lines like *****
            r'\|[\s\|-]+\|',   # Empty MD tables like | | | | --- | --- |
            r'\(Ban hành kèm theo.*\)', # Transition info
        ]
        
        lines = text.split('\n')
        clean_lines = []
        for line in lines:
            line_strip = line.strip()
            # Skip signature blocks and empty tables
            if any(re.search(p, line_strip, re.IGNORECASE) for p in signature_patterns):
                continue
            # Skip lines that are just dashes or stars
            if re.match(r'^[-\*\s\._\\]+$', line_strip):
                continue
            clean_lines.append(line)
            
        result = "\n".join(clean_lines).strip()
        
        # 3. De-noise internal asterisks (N****Ẵ****NG -> NẴNG)
        vn_chars = r'a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠ-ỹ'
        result = re.sub(fr'([{vn_chars}])\*+([{vn_chars}])', r'\1\2', result)
        
        # 4. Final polish: remove double Article headers if any nearby
        # (This helps when Article is both a header and in text)
        result = re.sub(r'(\*\*Điều \d+[:\.]\*\*)\s+\1', r'\1', result)
        
        return result

    def _recursive_split(self, text, max_size):
        if len(text) <= max_size:
            return [text]
        
        # Try to split by Khoản (e.g., "\n1. ", "\n2. ")
        clauses = re.split(r'(\n\d+\. )', text)
        if len(clauses) > 1:
            chunks = [clauses[0]]
            for i in range(1, len(clauses), 2):
                chunks.append(clauses[i] + clauses[i+1])
            
            # Further split if clauses are still too big
            final_chunks = []
            for c in chunks:
                if len(c) > max_size:
                    final_chunks.extend(self._simple_split(c, max_size))
                else:
                    final_chunks.append(c)
            return final_chunks
        
        return self._simple_split(text, max_size)

    def _simple_split(self, text, max_size):
        if len(text) <= max_size:
            return [text]
            
        chunks = []
        start = 0
        while start < len(text):
            if len(text) - start <= max_size:
                chunks.append(text[start:].strip())
                break
                
            end = start + max_size
            chunk_slice = text[start:end]
            
            split_at = -1
            
            last_para = chunk_slice.rfind('\n\n')
            if last_para > (max_size * 0.3):
                split_at = last_para
            else:
                last_newline = chunk_slice.rfind('\n')
                if last_newline > (max_size * 0.4):
                    split_at = last_newline
                else:
                    last_period = chunk_slice.rfind('. ')
                    if last_period > (max_size * 0.5):
                        split_at = last_period + 1
                    else:
                        last_space = chunk_slice.rfind(' ')
                        if last_space > (max_size * 0.7):
                            split_at = last_space
                            
            if split_at != -1:
                chunks.append(text[start:start + split_at].strip())
                start += split_at
            else:
                chunks.append(text[start:end].strip())
                start += max_size - self.chunk_overlap
                
        return [c for c in chunks if c]
