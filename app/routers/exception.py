from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request


class PerfectException(HTTPException):
    pass


class TooPerfectException(HTTPException):
    pass


def perfect_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "hi"})
