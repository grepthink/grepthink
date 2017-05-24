# Git Workflow
### Teamwork Project

#### Goal: define a team-wide git workflow to minimize conflicts

## How 2 GrepThink

```bash
# Keep your branch up to date with master to avoid an auto-merge fail
git checkout master
git pull
git checkout my-helpful-branch-name
git merge master

# Migration files are not tracked due to rapid development; to be safe, name all apps after a pull
python manage.py makemigrations auth profiles projects courses core
python manage.py migrate
python manage.py runserver

# Commit and push to remote often
# Optionally be awesome; commit without -m so you can
#  add details to your commit message [1].
git add -A
git commit -m "Add How 2 GrepThink to docs"
git push

# Compare your branch to master before you merge, here or on github
git diff master my-helpful-branch-name --minimal

# Open a pull request or if you think you're hot stuff
git merge master
```
[1] [Suggested commit message style](https://github.com/erlang/otp/wiki/Writing-good-commit-messages).


#### Example commit message
```
Add introspective commit example

Ponder the purpose of a commit message.

Understand the choice to prefer imperative commit titles. 
See how it is not easy to write as if you are:

- commanding someone
- barking orders
- a robot

Find some comfort in the fact that this choice increases:

- [x] consistency
- [x] readability
- [x] your git etiquette level
- [ ] the quality of your code
```

## Migration Files

### Early Development:
- Rapid changes to database models and many feature branches results in too many conflicts.
- The _migrations_ folders are ignored completely.
- Each developer has his own (possibly unique) migration files that are never committed master.

#### After a pull or merge, each developer must:
1. Make migrations (models may have been edited)
    `python manage.py makemigrations`
2. Migrate
    'python manage.py migrate'

Note: Initially you may have to reset migrations if you are getting errors. 
See [Resetting Django migrations in development phase](https://www.techiediaries.com/how-to-reset-migrations-in-django-17-18-19-and-110/).

#### Resources
- [Method used to untrack files already tracked by git](http://stackoverflow.com/a/1139797).

### Production
Ideally we'll switch to something like this once the production server/database is in use:
- Keep clean copies of the migration files in master.
- One persons runs `makemigrations` after an approved merge or pull request.
- Developers delete their migration files before a merge or pull request.
- Or [possibly](http://stackoverflow.com/questions/28035119/should-i-be-adding-the-django-migration-files-in-the-gitignore-file) [setup](http://stackoverflow.com/questions/22367353/git-merge-with-ignored-migrations-files) a [merge strategy](https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes#Merge-Strategies) that always prefers the migrations in master (developers would still have to make sure to delete newly auto generated migration files before merging).





# Helpful Git Commands

Visual representation of branches (similar to the [network graph on GitHub](https://github.com/andgates/teamwork-project/network)):
```bash
$ git log --oneline --all --graph --decorate
```

List all remote branches:
```bash
$ git branch -r
```

Remove stale remote branches:
```bash
$ git remote prune origin
```

Delete a local branch:
```bash
$ git branch -d branch-name
```

Force delete a local branch if not merged:
```bash
$ git branch -D branch-name
```
