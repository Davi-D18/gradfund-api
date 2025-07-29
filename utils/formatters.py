class StringFormatter:
    """Classe utilitária para formatação de strings"""
    
    @staticmethod
    def format_text(value, format_type='title'):
        """Formata texto removendo espaços e aplicando formatação"""
        if not value:
            return value
        
        cleaned_value = value.strip()
        
        if format_type == 'title':
            return cleaned_value.title()
        elif format_type == 'upper':
            return cleaned_value.upper()
        elif format_type == 'lower':
            return cleaned_value.lower()
        
        return cleaned_value