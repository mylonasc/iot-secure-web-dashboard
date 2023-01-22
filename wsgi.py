from app import app
 
if __name__ == "__main__":
    try:
        app.run()
    except Exception as e:
        with open('/tmp/exceptions-flask','w') as f:
            f.write(str(e))

