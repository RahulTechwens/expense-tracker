from fastapi.responses import JSONResponse
from fastapi import HTTPException
import json
import re
from app.models.expense_model import Expense
from datetime import datetime

import google.generativeai as genai  # type: ignore


class AIParseSmsController:
    @staticmethod
    async def sms_pasring(request, user):
        try:
            request_data = await request.json()
            results = []  # Collect all successfully parsed results
            errors = []   # Collect errors for skipped messages

            for count, item in enumerate(request_data["message"], start=1):
                sms_msg = item.get('sms_msg')
                if sms_msg:
                    try:
                        result = await AIParseSmsController.parse_sms(sms_msg, user, count)
                        if result != "null":
                            results.append(result)  # Collect the successful result
                        else:
                            errors.append(result)
                    except Exception as e:
                        # If any error occurs, log it and continue with the next SMS
                        errors.append(result)

            return JSONResponse(
                status_code=200,
                content={
                    "status": True,
                    "message": "SMS parsed successfully with some errors" if errors else "All SMS parsed successfully",
                    "results": results, 
                    "errors": errors   
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def extract_keys(sample_message):
        genai.configure(api_key="AIzaSyC6VDKKRSpiqNB5d8SmutvWkgA13wx11yo")
        model = genai.GenerativeModel("gemini-1.5-flash")
        command_1 = ". Please extract the following information from the provided text in simple text format: Account Number: The numerical identifier of the account as acct_no. Type: Whether the transaction was 'debited' or 'credited' as type. Transaction Date: The date of the transaction in ISO 8601 format (YYYY-MM-DD) as date. Merchant: The name or identifier of the entity involved in the transaction as merchant. Bank Name: The name of the bank associated with the transaction as bank_name. Transaction amount in float as amount. category of transaction like electronics, grocery, shopping, utilities, health, food&drink, entertainment, travel, Other, If not found then keep category Banking, as cat. Method is the transaction method like UPI or Bank Transfer as method. If any data is not present keep the value of that field N/A. Please provide to the point data please avoid redundant descriptions"
        prompt = f"{sample_message}{command_1}"

        response = model.generate_content(prompt)
        return response.text

    @staticmethod
    def generate_slug(merchant_name):
        if merchant_name == "N/A":
            return "N/A"
        else:
            merchant_name = merchant_name.lower()
            merchant_name = re.sub(r'[\s\-]+', '_', merchant_name)
            merchant_slug = re.sub(r'[^\w_]', '', merchant_name)
            return merchant_slug

    @staticmethod
    def add_expense(extracted_data, user):
        expense = Expense(
            cat=extracted_data.get("cat"),
            merchant=extracted_data.get("merchant"),
            merchant_slug=AIParseSmsController.generate_slug(extracted_data.get("merchant")),
            acct=extracted_data.get("acct_no"),
            bank=extracted_data.get("bank_name"),
            date=extracted_data.get("date"),
            amount=float(extracted_data.get("amount")),
            type=extracted_data.get("type"),
            method=extracted_data.get("method"),
            manual=False,
            user_phone=user['phone']
        )
        expense.save()  
        return str(expense.id)  

    @staticmethod
    async def parse_sms(sample_message, user, count):
        result_text = AIParseSmsController.extract_keys(sample_message)

        cleaned_text = result_text.strip("```json\n").strip("```").strip()

        extracted_data = None
        try:
            extracted_data = json.loads(cleaned_text)
        except json.JSONDecodeError:
            if count < 6:
                return await AIParseSmsController.parse_sms(sample_message, user, count + 1)
            else:
                return "null"
            

        if extracted_data:
            result = AIParseSmsController.add_expense(extracted_data, user)
            # return result
        else:
            raise HTTPException(
                status_code=500, detail="Failed to parse AI response."
            )
            
        return extracted_data