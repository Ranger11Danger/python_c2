tmux new-session -d -s "c2-testing"
tmux split-window -v -t "c2-testing"
tmux select-pane -t 0
tmux split-window -h -t "c2-testing"
tmux select-pane -t 0
tmux send-keys -t "c2-testing" "python3 c2.py --ip 127.0.0.1 --port 4444" Enter
sleep .5
tmux select-pane -t 1
tmux send-keys -t "c2-testing" "python3 payloads/test_payload.py" Enter
sleep .5
tmux select-pane -t 2
tmux send-keys -t "c2-testing" "python3 console.py" Enter
tmux send-keys -t "c2-testing" "set debug true" Enter
tmux send-keys -t "c2-testing" "connect --ip 127.0.0.1" Enter
tmux send-keys -t "c2-testing" "get_clients" Enter
tmux send-keys -t "c2-testing" "select 0" Enter
tmux attach -t "c2-testing"
