# Build stage
FROM public.ecr.aws/lambda/python:3.9 AS builder

# Copy requirements.txt
COPY requirements.txt .

# Install the specified packages
RUN pip install --no-cache-dir -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Runtime stage
FROM public.ecr.aws/lambda/python:3.9

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Copy dependencies from builder stage
COPY --from=builder ${LAMBDA_TASK_ROOT} ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler function
CMD [ "lambda_function.lambda_handler" ]