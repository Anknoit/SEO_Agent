import re
from typing import Dict, List, Tuple
import math

class SEOAnalyzer:
    def __init__(self):
        pass
    
    def analyze_page(self, page_data: Dict) -> Dict:
        """Comprehensive SEO analysis"""
        analysis = {
            'basic_metrics': self._get_basic_metrics(page_data),
            'title_analysis': self._analyze_title(page_data.get('title', '')),
            'meta_description_analysis': self._analyze_meta_description(page_data.get('meta_description', '')),
            'content_analysis': self._analyze_content(page_data.get('content', '')),
            'header_analysis': self._analyze_headers(page_data.get('headers', {})),
            'image_analysis': self._analyze_images(page_data.get('images', [])),
            'link_analysis': self._analyze_links(page_data.get('links', [])),
            'technical_seo': self._analyze_technical(page_data),
            'score': 0
        }
        
        # Calculate overall score
        analysis['score'] = self._calculate_seo_score(analysis)
        
        return analysis
    
    def _get_basic_metrics(self, page_data):
        content = page_data.get('content', '')
        title = page_data.get('title', '')
        description = page_data.get('meta_description', '')
        
        return {
            'word_count': len(content.split()),
            'title_length': len(title),
            'description_length': len(description),
            'image_count': len(page_data.get('images', [])),
            'link_count': len(page_data.get('links', [])),
            'response_time': page_data.get('response_time', 0)
        }
    
    def _analyze_title(self, title):
        length = len(title)
        analysis = {
            'current': title,
            'length': length,
            'optimal': 50 <= length <= 60,
            'issues': []
        }
        
        if length < 50:
            analysis['issues'].append(f"Title too short ({length} chars). Aim for 50-60 characters.")
        elif length > 60:
            analysis['issues'].append(f"Title too long ({length} chars). Aim for 50-60 characters.")
        
        if not title:
            analysis['issues'].append("Missing title tag")
        
        return analysis
    
    def _analyze_meta_description(self, description):
        length = len(description)
        analysis = {
            'current': description,
            'length': length,
            'optimal': 120 <= length <= 160,
            'issues': []
        }
        
        if length < 120:
            analysis['issues'].append(f"Description too short ({length} chars). Aim for 120-160 characters.")
        elif length > 160:
            analysis['issues'].append(f"Description too long ({length} chars). Aim for 120-160 characters.")
        
        if not description or description == "No meta description":
            analysis['issues'].append("Missing meta description")
        
        return analysis
    
    def _analyze_content(self, content):
        words = content.split()
        word_count = len(words)
        
        # Calculate readability (simple Flesch-like score)
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = word_count / max(len(sentences), 1)
        
        # Keyword density (simple version)
        text_lower = content.lower()
        common_words = ['seo', 'website', 'page', 'content', 'digital', 'marketing']
        keyword_density = {}
        
        for word in common_words:
            count = text_lower.count(word)
            if count > 0:
                density = (count / word_count) * 100
                keyword_density[word] = round(density, 2)
        
        analysis = {
            'word_count': word_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'keyword_density': keyword_density,
            'issues': []
        }
        
        if word_count < 300:
            analysis['issues'].append(f"Content too short ({word_count} words). Aim for at least 300 words.")
        
        if avg_sentence_length > 25:
            analysis['issues'].append(f"Sentences may be too long (avg: {avg_sentence_length:.1f} words).")
        
        return analysis
    
    def _analyze_headers(self, headers):
        analysis = {
            'structure': {},
            'issues': []
        }
        
        # Check for H1
        h1_count = len(headers.get('h1', []))
        if h1_count == 0:
            analysis['issues'].append("Missing H1 tag")
        elif h1_count > 1:
            analysis['issues'].append(f"Multiple H1 tags found ({h1_count})")
        
        # Count all headers
        for level in range(1, 7):
            count = len(headers.get(f'h{level}', []))
            analysis['structure'][f'h{level}'] = count
        
        # Check header hierarchy
        if h1_count == 0 and any(len(headers.get(f'h{i}', [])) > 0 for i in range(2, 7)):
            analysis['issues'].append("Header hierarchy issue: Using H2+ without H1")
        
        return analysis
    
    def _analyze_images(self, images):
        total_images = len(images)
        images_with_alt = sum(1 for img in images if img.get('has_alt', False))
        alt_percentage = (images_with_alt / total_images * 100) if total_images > 0 else 0
        
        analysis = {
            'total_images': total_images,
            'images_with_alt': images_with_alt,
            'alt_percentage': round(alt_percentage, 1),
            'issues': []
        }
        
        if total_images > 0 and alt_percentage < 90:
            analysis['issues'].append(f"Only {alt_percentage:.1f}% of images have alt text")
        
        return analysis
    
    def _analyze_links(self, links):
        total_links = len(links)
        internal_links = sum(1 for link in links if link.get('is_internal', False))
        external_links = total_links - internal_links
        
        broken_links = []  # Would need actual checking
        link_texts = [link.get('text', '') for link in links]
        empty_link_texts = sum(1 for text in link_texts if not text.strip())
        
        analysis = {
            'total_links': total_links,
            'internal_links': internal_links,
            'external_links': external_links,
            'empty_link_texts': empty_link_texts,
            'issues': []
        }
        
        if empty_link_texts > 0:
            analysis['issues'].append(f"{empty_link_texts} links with empty anchor text")
        
        if total_links > 0:
            internal_percentage = (internal_links / total_links) * 100
            if internal_percentage < 20:
                analysis['issues'].append(f"Low internal linking ({internal_percentage:.1f}%)")
        
        return analysis
    
    def _analyze_technical(self, page_data):
        issues = []
        
        # Check response time
        if page_data.get('response_time', 0) > 3:
            issues.append(f"Slow response time: {page_data['response_time']:.2f}s")
        
        return {
            'response_time': page_data.get('response_time', 0),
            'issues': issues
        }
    
    def _calculate_seo_score(self, analysis):
        score = 100
        
        # Deduct points for issues
        for category in ['title_analysis', 'meta_description_analysis', 'content_analysis', 
                        'header_analysis', 'image_analysis', 'link_analysis', 'technical_seo']:
            if category in analysis:
                issues = analysis[category].get('issues', [])
                score -= len(issues) * 2  # Deduct 2 points per issue
        
        # Content quality bonus
        if analysis['content_analysis']['word_count'] >= 300:
            score += 5
        
        # Image alt text bonus
        if analysis['image_analysis'].get('alt_percentage', 0) >= 90:
            score += 5
        
        return max(0, min(100, round(score)))