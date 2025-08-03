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
        elif format_type == 'strip':
            return cleaned_value
        
        return cleaned_value
    
    @staticmethod
    def clean_phone(value):
        """Remove caracteres especiais de números de telefone"""
        if not value:
            return value
        
        # Remove parênteses, espaços, hífens e underscores
        cleaned = value.replace('(', '').replace(')', '').replace(' ', '').replace('-', '').replace('_', '')
        return cleaned.strip()