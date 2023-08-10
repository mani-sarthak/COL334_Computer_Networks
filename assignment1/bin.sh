# #!/bin/bash

# lower_bound=1
# upper_bound=1024
# target_host="youtube.com"  # Replace with the target hostname or IP address

# while [ $lower_bound -lt $upper_bound ]; do
#     size=$(( ($lower_bound + $upper_bound) / 2 ))

#     # Run ping command with the current packet size
#     ping -c 1 -s $size $target_host >/dev/null 2>&1
#     # echo $upper_bound
#     if [ $? -eq 0 ]; then
#         lower_bound=$((size + 1))
#     else
#         upper_bound=$((size - 1))
#         if [ "$size" -eq 1 ]; then
#             echo "Error: Message too long for packet size $size"
#             exit 1
#         fi
#     fi
# done

# echo "Maximum packet size without 'Message too long' error: $upper_bound bytes"
#!/bin/bash

lower_bound=1
upper_bound=1024
target_host="youtube.com"  # Replace with the target hostname or IP address

while [ $lower_bound -lt $upper_bound ]; do
    size=$(( ($lower_bound + $upper_bound) / 2 ))

    # Run ping command with the current packet size
    output=$(ping -c 1 -s $size $target_host 2>&1)
    echo $output
    if [[ $output =~ "Message too long" ]]; then
        upper_bound=$((size - 1))
        if [ "$size" -eq 1 ]; then
            echo "Error: Message too long for packet size $size"
            exit 1
        fi
    else
        lower_bound=$((size + 1))
    fi
done

echo "Maximum packet size without 'Message too long' error: $upper_bound bytes"
