# transforms
Repository for various transforms that are common across CC projects.
(Just testing this right now...)

## Using in other projects

### Initializing 
This project is meant to be used as a subtree to other CC projects. 
Run the following commands in the project directory where you want _transforms_ to be created.

```
remote add -f transforms git@github.com:commoncriteria/transforms.git
git merge -s ours --no-commit transforms/master
git read-tree --prefix=transforms/ -u transforms/master
git commit -m "Transforms subtree merged into test"
```

### Updating

To pull changes from the transform project
```
git pull -s subtree transforms master
```

These commands were adapted from a
[github subtree tutorial](https://help.github.com/articles/about-git-subtree-merges/#adding-a-new-repository-as-a-subtree)


