mkdir -p service/proto
ln -s $(pwd)/service.proto ./service/proto/service.proto || true
python3 -m grpc_tools.protoc -I../proto --python_out=. --pyi_out=. --grpc_python_out=. service.proto