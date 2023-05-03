How to update lambda:

```bash
python zip.py      # Create new zip file for each lambda function.
python deploy.py   # Update the lambda function on localstack.
```

This is done for all functions. Maybe we could use a makefile to update only the
lambdas that have changed.