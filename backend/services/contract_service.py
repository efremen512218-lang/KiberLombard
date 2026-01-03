"""
Сервис генерации договоров и электронной подписи
"""
import hashlib
from datetime import datetime
from typing import Dict
from config import get_settings


class ContractService:
    """Сервис для работы с договорами"""
    
    @staticmethod
    def generate_contract_html(deal: Dict, user: Dict) -> str:
        """
        Генерировать HTML договора
        
        Args:
            deal: Данные сделки
            user: Данные пользователя
            
        Returns:
            HTML содержимое
        """
        settings = get_settings()
        
        # Форматирование предметов
        items_html = ""
        for i, item in enumerate(deal["items"], 1):
            name = item.get('name', item.get('market_hash_name', 'Unknown'))
            
            # Извлекаем цену (может быть dict или число)
            market_price_raw = item.get('market_price', 0)
            if isinstance(market_price_raw, dict):
                market_price = market_price_raw.get('instant_price', 0) or 0
            else:
                market_price = market_price_raw or 0
            
            instant_price_raw = item.get('instant_price', market_price)
            if isinstance(instant_price_raw, dict):
                instant_price = instant_price_raw.get('instant_price', 0) or 0
            else:
                instant_price = instant_price_raw or 0
            
            loan_price = float(instant_price) * 0.40  # 40% от цены
            items_html += f"""
            <tr>
                <td>{i}</td>
                <td>{name}</td>
                <td>{float(market_price):.2f} ₽</td>
                <td>{float(instant_price):.2f} ₽</td>
                <td>{loan_price:.2f} ₽</td>
            </tr>
            """
        
        # Расчёт выкупа
        term_config = deal.get("term_config", {})
        interest_amount = deal["loan_amount"] * term_config.get("interest", 0)
        premium_amount = (deal["loan_amount"] + interest_amount) * term_config.get("premium", 0)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Договор № {deal['id']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ text-align: center; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .section {{ margin: 30px 0; }}
                .signature {{ margin-top: 50px; }}
            </style>
        </head>
        <body>
            <h1>ДОГОВОР № {deal['id']}</h1>
            <h2>выкупа цифровых прав на внутриигровые предметы<br>с опционом на обратный выкуп</h2>
            <p><strong>Дата:</strong> {deal['created_at'].strftime('%d.%m.%Y')}</p>
            
            <div class="section">
                <h3>1. ПРЕДМЕТ ДОГОВОРА</h3>
                <p>Покупатель (ООО "КиберЛомбард") выкупает у Продавца ({user['full_name']}) 
                цифровые права на следующие внутриигровые предметы:</p>
                
                <table>
                    <tr>
                        <th>№</th>
                        <th>Наименование</th>
                        <th>Steam Market</th>
                        <th>Instant цена</th>
                        <th>Сумма выдачи</th>
                    </tr>
                    {items_html}
                    <tr>
                        <td colspan="4"><strong>ИТОГО:</strong></td>
                        <td><strong>{deal['loan_amount']:.2f} ₽</strong></td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h3>2. УСЛОВИЯ ВЫКУПА</h3>
                <p><strong>Срок опциона:</strong> {deal['option_days']} дней</p>
                <p><strong>Дата окончания:</strong> {deal['option_expiry'].strftime('%d.%m.%Y %H:%M МСК')}</p>
                <p><strong>Сумма обратного выкупа:</strong> {deal['buyback_price']:.2f} ₽</p>
                
                <h4>Расчёт суммы выкупа:</h4>
                <ul>
                    <li>Базовая сумма: {deal['loan_amount']:.2f} ₽</li>
                    <li>Процент за {deal['option_days']} дней ({term_config.get('interest', 0)*100:.0f}%): {interest_amount:.2f} ₽</li>
                    <li>Премия опциона ({term_config.get('premium', 0)*100:.0f}%): {premium_amount:.2f} ₽</li>
                    <li><strong>Итого к выкупу: {deal['buyback_price']:.2f} ₽</strong></li>
                </ul>
            </div>
            
            <div class="section">
                <h3>3. РИСКИ И ОГРАНИЧЕНИЯ</h3>
                <ul>
                    <li>Блокировки со стороны Steam/Valve: Платформа может заблокировать предметы или аккаунт. 
                    Покупатель не несёт ответственности за действия платформы.</li>
                    <li>Изменения правил: Steam может изменить правила трейда в любой момент.</li>
                    <li>Сохранность предметов: Покупатель не гарантирует сохранность предметов после передачи прав.</li>
                    <li>Прекращение права выкупа: После указанной даты выкупить предметы невозможно.</li>
                </ul>
            </div>
            
            <div class="section">
                <h3>4. ПОДПИСИ</h3>
                <p><strong>Покупатель:</strong> ООО "КиберЛомбард"</p>
                <p><strong>Продавец:</strong> {user['full_name']}</p>
                <p><strong>Паспорт:</strong> {user.get('passport_series', '')} {user.get('passport_number', '')}</p>
                
                <div class="signature">
                    <p><strong>Электронная подпись:</strong></p>
                    <p>Телефон: {ContractService._mask_phone(user['phone'])}</p>
                    <p>Дата: {deal.get('signature_timestamp', datetime.now()).strftime('%d.%m.%Y %H:%M:%S МСК')}</p>
                    <p>IP: {ContractService._mask_ip(deal.get('signature_ip', ''))}</p>
                    <p>Хэш договора: {deal.get('contract_hash', 'pending')}</p>
                </div>
            </div>
            
            <div class="section">
                <p><small>Версия договора: {settings.contract_version}</small></p>
                <p><small>Версия условий: {settings.terms_version}</small></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def calculate_hash(content: str) -> str:
        """Вычислить SHA-256 хэш содержимого"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    @staticmethod
    def _mask_phone(phone: str) -> str:
        """Замаскировать телефон"""
        if len(phone) >= 11:
            return f"+7{phone[2:5]}***{phone[-2:]}"
        return phone
    
    @staticmethod
    def _mask_ip(ip: str) -> str:
        """Замаскировать IP"""
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.***.***"
        return ip
    
    @staticmethod
    def generate_contract_pdf(deal: Dict, user: Dict, output_path: str) -> str:
        """
        Генерировать PDF договора с помощью reportlab
        
        Returns:
            Путь к сохранённому файлу
        """
        import os
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # Создаём папку contracts если не существует
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Создаём PDF
            doc = SimpleDocTemplate(output_path, pagesize=A4,
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
            
            styles = getSampleStyleSheet()
            story = []
            
            # Заголовок
            title_style = ParagraphStyle('Title', parent=styles['Heading1'], 
                                        fontSize=16, alignment=1, spaceAfter=20)
            story.append(Paragraph(f"DOGOVOR #{deal['id']}", title_style))
            story.append(Paragraph("Vykup tsifrovykh prav na vnutriigrovye predmety", 
                                  ParagraphStyle('Subtitle', parent=styles['Normal'], 
                                               fontSize=12, alignment=1, spaceAfter=20)))
            
            # Дата
            created = deal.get('created_at', datetime.now())
            if hasattr(created, 'strftime'):
                date_str = created.strftime('%d.%m.%Y')
            else:
                date_str = str(created)[:10]
            story.append(Paragraph(f"Data: {date_str}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Раздел 1 - Предмет договора
            story.append(Paragraph("1. PREDMET DOGOVORA", styles['Heading2']))
            story.append(Paragraph(
                f"Pokupatel (OOO KiberLombard) vykupaet u Prodavtsa ({user.get('full_name', 'Klient')}) "
                f"tsifrovye prava na sleduyushchie predmety:", styles['Normal']))
            story.append(Spacer(1, 10))
            
            # Таблица предметов
            items = deal.get('items', [])
            table_data = [['#', 'Nazvanie', 'Tsena', 'Vydacha']]
            
            for i, item in enumerate(items, 1):
                name = item.get('name', item.get('market_hash_name', 'Unknown'))[:30]
                price = item.get('instant_price', item.get('market_price', 0))
                if isinstance(price, dict):
                    price = price.get('instant_price', 0)
                loan = float(price) * 0.40
                table_data.append([str(i), name, f"{float(price):.0f} RUB", f"{loan:.0f} RUB"])
            
            table_data.append(['', 'ITOGO:', '', f"{deal.get('loan_amount', 0):.0f} RUB"])
            
            table = Table(table_data, colWidths=[1*cm, 8*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Раздел 2 - Условия
            story.append(Paragraph("2. USLOVIYA VYKUPA", styles['Heading2']))
            
            option_expiry = deal.get('option_expiry', datetime.now())
            if hasattr(option_expiry, 'strftime'):
                expiry_str = option_expiry.strftime('%d.%m.%Y')
            else:
                expiry_str = str(option_expiry)[:10]
            
            story.append(Paragraph(f"Srok optsiona: {deal.get('option_days', 14)} dney", styles['Normal']))
            story.append(Paragraph(f"Data okonchaniya: {expiry_str}", styles['Normal']))
            story.append(Paragraph(f"Summa vydachi: {deal.get('loan_amount', 0):.2f} RUB", styles['Normal']))
            story.append(Paragraph(f"Summa vykupa: {deal.get('buyback_price', 0):.2f} RUB", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Раздел 3 - Подписи
            story.append(Paragraph("3. PODPISI", styles['Heading2']))
            story.append(Paragraph(f"Pokupatel: OOO KiberLombard", styles['Normal']))
            story.append(Paragraph(f"Prodavets: {user.get('full_name', 'Klient')}", styles['Normal']))
            story.append(Paragraph(f"Steam ID: {user.get('steam_id', '')}", styles['Normal']))
            
            sig_time = deal.get('signature_timestamp', datetime.now())
            if hasattr(sig_time, 'strftime'):
                sig_str = sig_time.strftime('%d.%m.%Y %H:%M')
            else:
                sig_str = str(sig_time)[:16]
            story.append(Paragraph(f"Data podpisaniya: {sig_str}", styles['Normal']))
            
            # Генерируем PDF
            doc.build(story)
            print(f"[CONTRACT] PDF sozdan: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"[CONTRACT] Oshibka PDF: {e}")
            # Fallback на HTML
            html = ContractService.generate_contract_html(deal, user)
            html_path = output_path.replace('.pdf', '.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return html_path
