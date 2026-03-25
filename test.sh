# Clear any previous state
python3 tool.py clear

echo "===START TEST FOR USER - john==="

# Test rate limiting
for i in {1..15}; do
  echo "Request $i: "
  python3 tool.py request john
  sleep 0.5
done

# Check status
echo "===STATUS==="
python3 tool.py status john

echo "===LIST==="
# List all clients
python3 tool.py list

echo "===STATE FILE==="
# Check state file in current folder
ls -la state.json
