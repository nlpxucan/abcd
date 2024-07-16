# 📢 Distributed Fine-tuning   
We've conducted distributed fine tune experiment on our WizardLM utilizing original Llama-X project. Give the same hyperparameter as the Fine-tuning section, we expand our experiment on multi nodes.
To reproduce our experiments, we provided the steps and system configuration here.

## Steps
We assume you have worker-0, worker-1, worker-2 which are GPU nodes to be used for training and they could ssh into each other via private key. We assume worker-0 is the master node here, which has an opened port MASTER_PORT that worker-1 and worker-2 can directly access and it has a MASTER_IP that other nodes can access.

In each worker, configure your environment using the instructions in Llama-X. Different workers should use the same absolute path in your data, output, code folder and they should be exactly the same configuration.

After that, we need to change the hostfile config(*/path/to/Llama-X/src/configs/hostfile*) in each node, and add each worker into it, assuming 8 GPUs on each worker:
```bash
worker-0 slots=8
worker-1 slots=8
worker-2 slots=8
```

And since there might be some NCCL communication problem considering the complexity of every cluster, we recommend use this config:
```bash
NCCL_DEBUG=INFO
NCCL_ASYNC_ERROR_HANDLING=1
NCCL_BUFFSIZE=2097152
```
The good way is to write those variable into each nodes "*.deepspeed_env*" file in your home folder. You can refer this source for how-to: [multi-node-environment-variables](https://www.deepspeed.ai/getting-started/#multi-node-environment-variables)

Finally, everything is set up and run this command in worker-0. Enjoy your flight!
```bash
deepspeed --num_gpus 8 \
    --num_nodes 2 \
    --master_addr $MASTER_IP \
    --master_port $MASTER_PORT \
    --hostfile /path/to/Llama-X/src/configs/hostfile \
    train_freeform.py \
    --model_name_or_path /path/to/llama-7B/hf \
    --data_path /path/to/alpaca_evol_instruct_70k.json \
    --output_dir /path/to/wizardlm-7B/hf/ft \
    --num_train_epochs 3 \
    --model_max_length 2048 \
    --per_device_train_batch_size 8 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 1 \
    --evaluation_strategy "no" \
    --save_strategy "steps" \
    --save_steps 800 \
    --save_total_limit 3 \
    --learning_rate 2e-5 \
    --warmup_steps 2 \
    --logging_steps 2 \
    --lr_scheduler_type "cosine" \
    --report_to "tensorboard" \
    --gradient_checkpointing True \
    --deepspeed configs/deepspeed_config.json \
    --fp16 True
```

## Troubleshooting
Here are some common problem we could see from the console output:
1. "Call to ibv_reg_mr failed"
2. "ib_plugin.c:670 NCCL WARN NET/IB : Got completion with error 12, opcode 0, len 0, vendor err 129"   

As long as you have IB in your system, this problem could be triggered by missed configuration of ulimit.  If you run your experiment in a docker container, this option could be used for unlock ulimit limitation. 
```bash
docker ... --ulimit memlock=-1
```
Or you can use this solution from NCCL official document [troubleshooting.html#infiniband](https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/troubleshooting.html#infiniband) and make sure you login each worker as ROOT user or use root privilege to break the limitation.

The other issue is that you don't have IB and only have normal network card in each worker, you can use those config in *.deepspeed_env* to disable IB and use network to communicate:
```bash
NCCL_DEBUG=INFO
NCCL_P2P_DISABLE=1
NCCL_ASYNC_ERROR_HANDLING=1
NCCL_IB_DISABLE=1
NCCL_SOCKET_IFNAME=ens9f1
```
NCCL_SOCKET_IFNAME needs to be changed to your worker's actual network interface name, using *ifconfig* to find out.
