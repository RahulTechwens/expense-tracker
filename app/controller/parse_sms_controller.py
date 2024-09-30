from fastapi.responses import JSONResponse
from fastapi import HTTPException
import re
from app.models.expense_model import Expense
from datetime import datetime

class ParseSmsController:
    categories = {
        "Banking": [
            "credited",
            "debited",
            "balance",
            "account",
            "payment",
            "UPI",
            "cr",
            "dr",
        ],
        "Shopping": ["purchase", "spent", "at", "store", "mall"],
        "Utilities": ["bill", "electricity", "water", "internet", "phone"],
        "Insurance": ["insurance", "premium"],
        "Entertainment": ["movie", "tickets"],
        "Recharge": ["recharge", "mobile"],
    }

    pattern = r"([A-Za-z\s]+(?:Bank|BOB|SBI)|-SBI)"
    # pattern = r"([A-Za-z\s]+(?:Bank|BOB|SBI))"
    # pattern = r"([A-Za-z\s]+(?:Bank|BOB))"

    regex_for_sms_parsing = r"(?:Acct|A\/c|Account|A\/C|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))"

    async def parsing_sms(self, request, user):
        try:
            request_data = await request.json()
            for item in request_data["message"]:
                # Access 'sms_msg' properly using item.get('sms_msg')
                parsed_text = await self.filtering_sms(item.get('sms_msg'))
                
                # Access 'sms_msg' properly in re.findall as well
                parsed_bank = re.findall(
                    self.pattern, item.get('sms_msg'), re.IGNORECASE
                )
                # return parsed_bank
                parsed_message = self.get_parsed_sms(parsed_bank, item.get('sms_msg'), parsed_text, user)

            return JSONResponse(
                status_code=200,
                content={
                    "status": True,
                    "message": "Sms parsed successfully",
                    # "id": parsed_message
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def filtering_sms(message: str):
        message_lower = message.lower()
        for category, keywords in ParseSmsController.categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        return "Other"
    
    @staticmethod
    def generate_slug(merchant_name):
        merchant_name = merchant_name.lower()
        merchant_name = re.sub(r'[\s\-]+', '_', merchant_name)
        merchant_slug = re.sub(r'[^\w_]', '', merchant_name)
        return merchant_slug
    
    @staticmethod
    def insert_sms_data(cat,account_number,bank,current_date,amount,transaction_type, user):
        expense = Expense(
            cat=cat,
            merchant="",
            merchant_slug="",
            acct=account_number,
            bank=bank,
            date=current_date,
            amount=amount,
            type=transaction_type,
            method = "N/A",
            manual= False,
            user_phone=user['phone']
        )

        expense.save()  
        return str(expense.id)

    @staticmethod
    def generate_slug(merchant_name):
        merchant_name = merchant_name.lower()
        merchant_name = re.sub(r"[\s\-]+", "_", merchant_name)
        merchant_slug = re.sub(r"[^\w_]", "", merchant_name)
        return merchant_slug


    @staticmethod
    def get_parsed_sms(parsed_bank_name: list, message: str, parsed_text: str, user):
        today = datetime.today()
        formatted_date = today.strftime('%Y-%m-%d')
        
        if any(
            bank in parsed_bank_name for bank in ["Team IDFC FIRST Bank", "ICICI Bank"]
        ):
            regex_for_sms_parsing = r"(?:Acct|A\/c|Account|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?from\s*([\w\s]+))?"
            regex_for_sms_parsing_1 = r"Acct\s+(\w+)\s+(debited|credited)\s+for\s+(?:INR|Rs\.?)\s*([\d,]+\.\d{2})\s+on\s+\d{2}-\w{3}-\d{2};\s+([\w\s]+)\s+(?:credited|debited)"
            # regex_for_sms_parsing = r"(?:Acct|A\/c|Account|A\/C|A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited|CREDITED|DEBITED)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))"
            # regex_for_sms_parsing = r"(?:Acct|A\/c|Account|   A\/C|a\/c|a\/C)[*\s]*(\w+)\s*(?:is|has been)?\s*(credited|debited)\s*(?:with)?\s*(?:INR|Rs\.?)\s*([\d,]+\.\d{2})(?:.*?(?:Team|UPI:.*?-))?\s*([\w\s]+(?:Bank|BANK|bank))"

            parsed_msg = re.search(regex_for_sms_parsing, message, re.IGNORECASE)
            if parsed_msg:
                account_number = parsed_msg.group(1)
                type_msg = parsed_msg.group(2)
                amount = parsed_msg.group(3)
                merchant_name = parsed_msg.group(4)  # Capturing the merchant's name
                
                # return {
                #     "a":account_number,
                #     "b":type_msg,
                #     "c":amount,
                #     "d":merchant_name
                # }
                expense = Expense(
                    cat = parsed_text,
                    merchant = "Unknown",
                    merchant_slug=ParseSmsController.generate_slug("Unknown"),
                    acct = account_number if account_number else '',
                    bank = parsed_bank_name if parsed_bank_name else 'Unknown',
                    date = formatted_date,
                    amount =  float(amount[0]) if amount else '',
                    type = type_msg[0] if type_msg else '',
                    method = "N/A",
                    manual= False,
                    user_phone=user['phone'],
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                expense.save()
                return str(expense.id)
            
            
            
            parsed_msg = re.search(regex_for_sms_parsing_1, message)
            if parsed_msg:
                account_number = parsed_msg.group(1)
                transaction_type = parsed_msg.group(2)
                amount = parsed_msg.group(3)
                merchant_name = parsed_msg.group(4)
                
                expense = Expense(
                    cat=parsed_text,
                    merchant=merchant_name if merchant_name else 'Unknown',
                    merchant_slug=ParseSmsController.generate_slug(merchant_name if merchant_name else "Unknown"),  # Passing merchant_name if available, else "Unknown"
                    acct=account_number if account_number else '',
                    bank = parsed_bank_name[0] if parsed_bank_name else 'Unknown',
                    date=formatted_date,
                    amount=float(amount) if amount else '',
                    type=transaction_type[0] if transaction_type else '',
                    method="N/A",
                    manual=False,
                    user_phone=user['phone']
                )
                expense.save()
                return str(expense.id)
            
            else:
                return {"error": "Failed to parse SMS details"}
            
            
            
            
        elif any(bank in parsed_bank_name for bank in [" From HDFC Bank"]):
            regex_for_hdfc = r"Amt\s(Sent|Received)\sRs\.(\d+\.?\d*)\sFrom\s([A-Z\s]+)\sBank\sA\/C\s\*([0-9]{4})\sTo\s([A-Za-z-]+)"

            parsed_msg = re.search(regex_for_hdfc, message, re.IGNORECASE)

            if parsed_msg:
                transaction_type=(
                    "credit" if parsed_msg.group(1) == "Sent" else "debit"
                ),
                amount=parsed_msg.group(2)
                account_number=parsed_msg.group(4)
                recipient=parsed_msg.group(5)
                
                expense = Expense(
                    cat = parsed_text,
                    merchant = recipient if recipient else 'Unknown',
                    merchant_slug=ParseSmsController.generate_slug(recipient if recipient else 'Unknown'),
                    acct = account_number if account_number else '',
                    bank = parsed_bank_name[0] if parsed_bank_name[0] else 'Unknown',
                    date = formatted_date,
                    amount =  float(amount[0]) if amount else '',
                    type = transaction_type[0] if transaction_type[0] else '',
                    method = "",
                    manual= False,
                    user_phone=user['phone'],
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    
                )
                expense.save()
                return str(expense.id)
            else:
                return {"error": "Failed to parse SMS details"}
            
            
            
        elif any(bank in parsed_bank_name for bank in [" Indian Bank", "Indian Bank"]):
            regex_for_indian_bank = r"A\/c \*([0-9]{4})\s(debited|credited)\sRs\.\s([\d,]+(?:\.\d{2})?)\s+on\s(\d{2}-\d{2}-\d{2})\s+to\s([A-Za-z\-]+)\."
            regex_for_indian_bank_1 = r"Rs\.(\d+\.\d+) (credited|debited) to a\/c \*(\d+) on (\d{2}\/\d{2}\/\d{4}) by a\/c linked to VPA (\S+) \(UPI Ref no \d+\)\. Dial \d+ for Cyber Fraud -Indian Bank"

            parsed_msg = re.search(regex_for_indian_bank, message, re.IGNORECASE)
            if parsed_msg:
                account_number=parsed_msg.group(1)
                transaction_type=parsed_msg.group(2)
                amount=parsed_msg.group(3)[0]
                recipient=parsed_msg.group(5)
                
                expense = Expense(
                    cat = parsed_text,
                    merchant = recipient if recipient else 'Unknown',
                    merchant_slug=ParseSmsController.generate_slug(recipient if recipient else 'Unknown'),
                    acct = account_number if account_number else '',
                    bank = parsed_bank_name[0] if parsed_bank_name[0] else 'Unknown',
                    date = formatted_date,
                    amount =  float(amount[0]) if amount else '',
                    type = transaction_type if transaction_type else '',
                    method = "",
                    manual= False,
                    user_phone=user['phone'],
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    
                )
                expense.save()
                return str(expense.id)

            parsed_msg = re.search(regex_for_indian_bank_1, message, re.IGNORECASE)
            if parsed_msg:
                account_number=parsed_msg.group(1)
                transaction_type=parsed_msg.group(2)
                amount=parsed_msg.group(3)
                recipient=parsed_msg.group(5)
                
                
                expense = Expense(
                    cat = parsed_text,
                    merchant = recipient if recipient else '',
                    merchant_slug=ParseSmsController.generate_slug(recipient if recipient else 'Unknown'),
                    acct = account_number if account_number else '',
                    bank = parsed_bank_name[0] if parsed_bank_name[0] else '',
                    date = formatted_date,
                    amount =  float(amount[0]) if amount else '',
                    type = transaction_type if transaction_type else '',
                    method = "",
                    manual= False,
                    user_phone=user['phone'],
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                expense.save()
                return str(expense.id)

            return {"error": "Failed to parse SMS details"}
        elif any(bank in parsed_bank_name for bank in [" Canara Bank", "Canara Bank"]):
            regex_for_canara = {
                "transaction_type": r"(\bCREDITED\b|\bDEBITED\b)",
                "amount": r"INR\s([\d,]+\.\d{2})",
                "bank": r"\b([A-Za-z\s]+Bank)\b",
                "account_number": r"account\s(\w+)",
                "recipient": r"(?:your\saccount\s)(\w+)",
            }
            extracted_info = {}
            for key, pattern in regex_for_canara.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()
            recipient = extracted_info.get('recipient') 
            account_number =  extracted_info.get('account_number')
            amount =  extracted_info.get('amount') 
            transaction_type =  extracted_info.get('transaction_type')

            expense = Expense(
                cat = parsed_text,
                merchant = recipient if recipient else 'Unknown',
                merchant_slug=ParseSmsController.generate_slug(recipient if recipient else 'Unknown'),
                acct = account_number if account_number else '',
                bank = parsed_bank_name[0] if parsed_bank_name[0] else 'Unknown',
                date = formatted_date,
                amount =  float(amount) if amount else 0,
                type = transaction_type if transaction_type else '',
                method = "N/A",
                manual= False,
                keywords=[],
                vector=[],
                user_phone=user['phone'],
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                
            )
            expense.save()
            return str(expense.id)
        elif any(bank in parsed_bank_name for bank in [" Axis Bank", "Axis Bank"]):
            regex_for_axis = {
                "transaction_type": r"(credited|debited)",
                "amount": r"INR\s([\d,]+\.\d{2})",
                "account_number": r"A/c\sno\.\s([Xx*\d]+)",
                "bank": r"-\s([A-Za-z\s]+)\sBank",
                "recipient": r"Info-\s(?:UPI|P2A|IMPS)/[\d]+/([A-Za-z\s]+)",
                "date_time": r"on\s(\d{2}-\d{2}-\d{2,4})\sat\s([\d:]+)",
            }
            extracted_info = {}
            for key, pattern in regex_for_axis.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()
            expense = Expense(
                cat=parsed_text,
                merchant=extracted_info.get("recipient", "Unknown"),
                merchant_slug=ParseSmsController.generate_slug(extracted_info.get("recipient", "Unknown")),
                acct=extracted_info["account_number"],
                bank=extracted_info["bank"] or "Unknown",
                date=extracted_info["date_time"],
                amount=float(extracted_info["amount"]),
                type=extracted_info["transaction_type"],
                method = "N/A",
                manual= False,
                user_phone=user['phone'],
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                
                
            )
            expense.save()
            return str(expense.id)
        # elif any(bank in parsed_bank_name for bank in ["ICICIBank"]):
 
        #     regex_for_axis = {
        #         "transaction_type": r"(credited|debited)",
        #         "amount": r"Rs\s*([\d,]+\.\d{2})",
        #         "account_number": r"Acct\s*([Xx*\d]+)",
        #         "bank": r"([A-Za-z\s]+Bank)",  
        #         "recipient": r"Info-\s(?:UPI|P2A|IMPS)/[\d]+/([A-Za-z\s]+)",
        #     }
 
        #     extracted_info = {}
 
        #     for key, pattern in regex_for_axis.items():
        #         match = re.search(pattern, message)
        #         if match:
        #             extracted_info[key] = match.group(1).strip()
 
        #     expense = Expense(
        #         cat=parsed_text,
        #         merchant=extracted_info.get("recipient", "Unknown"),
        #         merchant_slug=ParseSmsController.generate_slug(extracted_info.get("recipient", "Unknown")),
        #         acct=extracted_info.get("account_number", ''),
        #         bank=extracted_info.get("bank", ''),
        #         date=formatted_date,
        #         amount=float(extracted_info.get("amount", '0.00').replace(',', '')),
        #         type=extracted_info.get("transaction_type", ''),  
        #         method="",
        #         manual=False,
        #         user_phone=user['phone']

        #     )
 
        #     expense.save()
 
        #     return str(expense.id)
        elif any(bank in parsed_bank_name for bank in ["ICICIBank"]):
 
            regex_for_icici = {
                "transaction_type": r"(credited|debited)",
                "amount": r"Rs\s*([\d,]+\.\d{2})",
                "account_number": r"Acct\s*([Xx*\d]+)",
                "bank": r"([A-Za-z\s]+Bank)",  
                "recipient": r"Info-\s(?:UPI|P2A|IMPS)/[\d]+/([A-Za-z\s]+)",
                "merchant":r";([^;]+)credited"
            }
 
            extracted_info = {}
 
            for key, pattern in regex_for_icici.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()
                    
            # merchant = extracted_info.get("merchant", "Unknown")
            # merchant_slug = ParseSmsController.generate_slug(merchant)
            # return merchant_slug
 
            expense = Expense(
                cat=parsed_text,
                merchant=extracted_info.get("merchant", "Unknown"),
                merchant_slug=ParseSmsController.generate_slug(extracted_info.get("merchant", "Unknown")),
                acct=extracted_info.get("account_number", 'N/A'),
                bank=extracted_info.get("bank", ''),
                date=formatted_date,
                amount=float(extracted_info.get("amount", '0.00').replace(',', '')),
                type=extracted_info.get("transaction_type", ''),  
                method="",
                manual=False,
                user_phone=user['phone']

            )
 
            expense.save()
            return str(expense.id)
        
        ####################################################################################### sbi
        elif any(bank in parsed_bank_name for bank in ["-SBI"]):
 
            regex_for_icici = {
                "transaction_type": r"(credited|debited)",
                "amount": r"Rs\s*([\d,]+\.\d{2})",
                "account_number": r"Acct\s*([Xx*\d]+)",
                "bank": r"([A-Za-z\s]+Bank)",  
                "merchant":r";([^;]+)credited"
            }
 
            extracted_info = {}
 
            for key, pattern in regex_for_icici.items():
                match = re.search(pattern, message)
                if match:
                    extracted_info[key] = match.group(1).strip()
                    
            # merchant = extracted_info.get("merchant", "Unknown")
            # merchant_slug = ParseSmsController.generate_slug(merchant)
            # return merchant_slug
 
            expense = Expense(
                cat=parsed_text,
                merchant=extracted_info.get("merchant", "Unknown"),
                merchant_slug=ParseSmsController.generate_slug(extracted_info.get("merchant", "Unknown")),
                acct=extracted_info.get("account_number", 'N/A'),
                bank=extracted_info.get("bank", ''),
                date=formatted_date,
                amount=float(extracted_info.get("amount", '0.00').replace(',', '')),
                type=extracted_info.get("transaction_type", ''),  
                method="",
                manual=False,
                user_phone=user['phone'],
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                

            )
 
            expense.save()
 
            return str(expense.id)
        
        
        ######################################################################################## sbi
        
        # elif any(
        #     bank in parsed_bank_name for bank in [" Bank of Baroda ", " Bank of Baroda "]
        # ):
        #     regex_for_axis = {
        #         "transaction_type": r"(Credited|Debited)",
        #         "amount": r"Rs\.(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)",
        #         "account_number": r"A/c\s\.\.\.\d{4}",
        #         "bank": r"-\s([A-Za-z\s]+)$",
        #         "recipient": r"by\s([a-zA-Z0-9._]+)",
        #         "date_time": r"\((\d{2}-\d{2}-\d{4})\s(\d{2}:\d{2}:\d{2})\)",
        #     }
        #     extracted_info = {}
        #     for key, pattern in regex_for_axis.items():
        #         match = re.search(pattern, message)
        #         if match:
        #             extracted_info[key] = match.group(1).strip()
        #     return extracted_info
        # # return None
    
        # else:
        #     expense = Expense(
        #         cat="",
        #         merchant="",
        #         acct="",
        #         bank="",
        #         date="",
        #         amount="",
        #         type="",
        #         method = "",
        #         manual= "",
        #         user_phone=user['phone']
                
        #     )
        #     expense.save()
        #     return str(expense.id)
        