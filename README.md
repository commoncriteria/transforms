# transforms
Repository for various transforms that are common across CC projects.
(Just testing this right now...)

## Using in other projects

### Initializing 
This project is meant to be used as a submodule to other CC projects. 
Run the following commands in the project directory where you want _transforms_ to be created.

```
git submodule add git@github.com:commoncriteria/transforms.git
git commit -am "Added the Transforms submodule to the project"
git push
```

### Pulling new updates from transforms

To pull changes from the transform project
```
git submodule update --remote transforms
```

### Make changes to a submodule
Within the submodule directory run the following command
```
git checkout master
git submodule update --remote --merge
```
Make changes like normal to the submodule files and then commit the changes.

### Pushing new updates to transforms submodule when in a parent project
Run inside the parent project.

```
git push --recurse-submodules=on-demand
```

These commands were adapted from the
[git-scm book](https://git-scm.com/book/en/v2/Git-Tools-Submodules).
