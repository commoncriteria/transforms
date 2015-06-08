# transforms
Repository for various transforms that are common across CC projects.
(Just testing this right now...)

## Using in other projects

### Initializing 
This project is meant to be used as a subtree to other CC projects. 
Run the following commands in the project directory where you want _transforms_ to be created.

```
git remote add -f transforms git@github.com:commoncriteria/transforms.git
git subtree add --prefix=transforms/ transforms master
git commit -m "Transforms subtree merged into test"
```

### Pulling new updates from transforms

To pull changes from the transform project
```
git pull -s subtree transforms master
```

### Pushing new updates to transforms
Run inside the parent project, but outside the subtree.

```
git subtree push --prefix transforms transforms master
```

These commands were adapted from a
[github subtree tutorial](https://help.github.com/articles/about-git-subtree-merges/#adding-a-new-repository-as-a-subtree)
.