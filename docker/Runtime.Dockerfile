FROM shadrinsergey/option_volatility_dashboard_base:0.0.1

WORKDIR /app

COPY src .

ENTRYPOINT ["python"]
CMD ["main.py"]