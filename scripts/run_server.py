import os
import sys
os.chdir('f:/college/sophomore/academic')
sys.path.insert(0, 'f:/college/sophomore/academic')
os.environ['PORT'] = '8002'

if __name__ == '__main__':
    import uvicorn
    print("Starting server on port 8002...")
    uvicorn.run('web.backend.main:app', host='0.0.0.0', port=8002, log_level='info')
