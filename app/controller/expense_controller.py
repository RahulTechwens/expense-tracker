from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request
from app.services.expense_service import ExpenseService
from ..helper.response_helper import ResponseServiceHelper 


class ExpenseController:
    async def create_expense(request: Request, user):
        try:
            print(user["phone"], "dgdjgy")
            request_data = await request.json()
            await ExpenseService.insert_expense(request_data, user)
            response_data = {"status": "success", "result": request_data}
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Expense recorded successfully",
                    "data": response_data,
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create_custom_cat(request: Request):
        try:
            request_data = await request.json()
            result = await ExpenseService.insert_custom_cat(request_data)
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Expense recorded successfully",
                    "data": result
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def cat_filter(cat, start_date, end_date, group_by, user):
        try:
            cat = cat.split(",") if cat else []
            start_date = start_date or None
            end_date = end_date or None
            group_by = group_by or None
            result = await ExpenseService.filter_sms_category(cat, start_date, end_date,group_by, user)
            return ResponseServiceHelper.success_helper(
                200,
                result
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def all_cat():
        try:
            result = await ExpenseService.show_all_cat()
            return JSONResponse(
                status_code=200,
                content={
                    "Message": "All Category Fetched Successfully",
                    "data": result,
                },
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def expense_gpt(request: Request):
        try:
            request_data = await request.json()
            await ExpenseService.expense_gpt_msg(request_data)
            response_data = {"status": "success", "Message": request_data}
            return JSONResponse(
                status_code=200,
                content={"message": "Message only", "data": response_data},
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def rename_custom_cat(request: Request):
        request_data = await request.json()
        result = await ExpenseService.rename_custom_cat(request_data)

        return JSONResponse(
            status_code=200,
            content = {"message": "The custom category renamed to " + result}
        )
        
    async def time_wise_expense(request: Request, user):
        request_data = await request.json()
        result = await ExpenseService.time_wise_expense(request_data, user)

        return ResponseServiceHelper.success_helper(
            200,
            {"message": "All data fetched successfully", "data": result}
        )

    async def graph_wise_expense(request: Request, user):
        try:
            request_data = await request.json()
            result = await ExpenseService.graph_filter(request_data, user)


            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def graph_wise_categories(request: Request, user):
        try:
            request_data = await request.json()
            result = await ExpenseService.graph_category(request_data, user)


            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def alter_cat(request: Request, user):
        try:
            request_data = await request.json()
            result = await ExpenseService.alter_cat(request_data, user)
            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    async def graph_data(type, user):
        try:
            # request_data = await request.json()
            result = await ExpenseService.graph(type, user)
            return ResponseServiceHelper.success_helper(
                200,
                result
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))