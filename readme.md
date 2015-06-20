# Ant

> This is just a toy

created with `asyncio`, `aiohttp` and `pyquery`. 

## Example

Here is a simple example


    from ant import Job
    def step1():
        print('Step:1')
        return list(range(10))
     
     
    def step2(x):
        print('step:2')
        return x * x
     
     
    def step3(x):
        print("Step:3")
        return [x, x]
     
    job = Job()
    job.init(step1).then(step2).then(step3).then(print).run()


## License

The whole repo using WTFPL License
