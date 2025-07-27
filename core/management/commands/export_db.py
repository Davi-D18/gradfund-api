import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection


class Command(BaseCommand):
    help = 'Exporta o banco de dados para um arquivo SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='database_export.sql',
            help='Nome do arquivo de saída (padrão: database_export.sql)'
        )
        parser.add_argument(
            '--with-data',
            action='store_true',
            help='Inclui os dados das tabelas na exportação'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        with_data = options['with_data']
        
        try:
            with connection.cursor() as cursor:
                with open(output_file, 'w', encoding='utf-8') as f:
                    self._export_structure(cursor, f)
                    if with_data:
                        self._export_data(cursor, f)
                        
            export_type = 'com dados' if with_data else 'apenas estrutura'
            self.stdout.write(
                self.style.SUCCESS(
                    f'Banco exportado ({export_type}) para: {output_file}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao exportar banco: {str(e)}')
            )
    
    def _export_structure(self, cursor, f):
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Ordena tabelas por dependências
        ordered_tables = self._order_tables_by_dependencies(cursor, tables)
        
        f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")
        
        for table in ordered_tables:
            cursor.execute(f"SHOW CREATE TABLE `{table}`")
            create_sql = cursor.fetchone()[1]
            f.write(f"{create_sql};\n\n")
            
        f.write("SET FOREIGN_KEY_CHECKS = 1;\n\n")
    
    def _order_tables_by_dependencies(self, cursor, tables):
        # Obtém dependências de chaves estrangeiras
        cursor.execute("""
            SELECT table_name, referenced_table_name
            FROM information_schema.key_column_usage
            WHERE table_schema = DATABASE() 
            AND referenced_table_name IS NOT NULL
        """)
        
        dependencies = {}
        for table, ref_table in cursor.fetchall():
            if table not in dependencies:
                dependencies[table] = set()
            dependencies[table].add(ref_table)
        
        # Ordenação topológica
        ordered = []
        remaining = set(tables)
        
        while remaining:
            # Encontra tabelas sem dependências não resolvidas
            ready = []
            for table in remaining:
                deps = dependencies.get(table, set())
                if not (deps & remaining):  # Sem dependências pendentes
                    ready.append(table)
            
            if not ready:
                # Adiciona tabelas restantes (ciclos ou problemas)
                ready = list(remaining)
            
            ordered.extend(sorted(ready))
            remaining -= set(ready)
        
        return ordered
    
    def _export_data(self, cursor, f):
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        # Usa a mesma ordenação para os dados
        ordered_tables = self._order_tables_by_dependencies(cursor, tables)
        
        for table in ordered_tables:
            cursor.execute(f"SELECT * FROM `{table}`")
            rows = cursor.fetchall()
            
            if rows:
                for row in rows:
                    values = []
                    for value in row:
                        if value is None:
                            values.append('NULL')
                        elif isinstance(value, str):
                            values.append(f"'{value.replace("'", "\\'")}'")
                        else:
                            values.append(str(value))
                    
                    f.write(f"INSERT INTO `{table}` VALUES ({','.join(values)});\n")
                f.write("\n")