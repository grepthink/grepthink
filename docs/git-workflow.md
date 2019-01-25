# Git workflow

## Cloning and forking the repository

1. **Clone the repository.** Click the green "<font color="green">Clone or download</font>" button,
   and copy the url and type
   
   <pre><code>git clone <i>clone-url</i></code></pre>

   at the terminal. Replace *`clone-url`* with the url that has been copied to
   your clipboard. For grepthink/grepthink, it will be
   `git@github.com:grepthink/grepthink.git`. If you have not set up your ssh keys with
   GitHub, use the https url by first clicking the `https` button.  

   *Note: It is important that you clone from the repo (grepthink/grepthink),* not *your fork of the repo.*

2. **Fork the repo on GitHub to your personal account.** Click the `Fork`
   button on the grepthink/grepthink page.      

3. **Add your fork as a remote.** This remote will be named after your github
   username.  Go to the fork of your repository, in this case,
   <code>https://github.com/<i>your-username</i>/grepthink</code> (replace *`your-username`* with
   your GitHub username), and copy the clone url as in step 1. `cd` to your
   clone from step 1 and run
   
   <pre><code>git remote add <i>your-github-username fork-url</i></code></pre>   

   (replace *`your-github-username`* with your GitHub username and
   *`fork-url`* with the url that was copied to your clipboard). You will be
   able to tell it is your fork url because it will have your GitHub username
   in it. For instance, if your username is `github_user`, you would run the
   command `git remote add github_user git@github.com:github_user/grepthink.git`.

Remember, the above three steps only need to be performed once. Once you have cloned and forked a repository once, there is no
need to clone or fork it again.

## Making changes

Before you make any changes, you should make a branch. Remember to **never
commit to master**. The command `git status` will tell you what branch you are
on. I recommend putting the git branch in your command prompt, so that you
will always know what branch you are on. See
[this guide](http://stackoverflow.com/a/24716445/161801) on how to do this.
Many terminal applications do this out of the box.

It is important that you never commit to master because master will be the
branch that you pull upstream changes from (e.g., changes from
grepthink/grepthink).

1. **Update master.** Before you make any changes, first checkout master

   ```
   git checkout master
   ```

   and pull in the latest changes

   ```
   git pull
   ```

   This will make it so that your changes are against the very latest master,
   which will reduce the likelihood of merge conflicts due to your changes
   conflicting with changes made by someone else.

2. **Create a branch.** Once you have done this, create a new branch. You
   should make a branch name that is short, descriptive, and unique. Some
   examples of good branch names are `fix-install`, `docs-cleanup`, and
   `add-travis-ci`. Some examples of bad branch names are `feature`, `fix`,
   and `patch`. The branch name choice is not too important, so don't stress
   over it, but it is what people will use to reference your changes if they
   want to pull them down on their own computers to test them, so a good name
   will make it easier for others to understand what your branch does. In this
   example, the branch name is `fix-install`.

   To create the branch, run

   <pre><code>git checkout -b <i>branch-name</i></code></pre>

   (replace *`branch-name`* with the branch name you chose). This will create a
   new branch and check it out. You can verify this with `git status`.

3. **Make your changes and commit them.** Once you have created your branch,
   make your changes and commit them. Remember to keep your commits atomic,
   that is, each commit should represent a single unit of change. Also,
   remember to write helpful commit messages, so that someone can understand
   what the commit does just from reading the message without having to read
   the diff.

   For example, at the command line, this might look like

   <pre><code>git add <i>filename [filename ...]</i>
   git commit
   </code></pre>

   This will open an editor where you can write your commit message.

4. **Push up your changes.**  Push your changes to your fork. Do this by
   running

   <pre><code>git push <i>your-github-username</i> <i>branch-name</i></code></pre>

5. **Make a pull request.** If you then go to your fork on GitHub, you should
   see a button to create a pull request from your branch.

   If you do not see this, go to the GitHub page for your fork, select the branch from the branch popup and click the pull request button.   

   Once doing this, you will be presented with a page. This page will show you
   the diff of the changes. Double check them to make sure you are making a
   pull request against the right branch.

   Things to check here are that the base fork is the upstream repo (in this case, grepthink/grepthink) and the branch for the
   upstream repo is master, and that the head fork is your fork and the branch is the branch you wish to make the
   pull request from.

   Enter a descriptive title in the title field and write a short description.    

   If the pull request fixes an issue, you can add "fixes #**1234**" (replace
   **1234** with the actual issue number) in the pull request description.
   This will link the issue to the Pull Request and close the issue when the PR is merged.

   Once you are done, click the "create pull request" button   

6. **Pushing additional changes**. Once you have created the pull request, it
   will likely be reviewed and some additional fixes will be necessary. **Do
   not create a new pull request.** Rather, simply make more commits to your
   branch and push them up as in steps 3 and 4. They will be added to the pull
   request automatically. It is a good idea to make a comment
   on the pull request whenever you do so to notify people that it is ready to
   be reviewed again.

Once the pull request has been reviewed successfully, someone with push access
to the main repository will merge it in. At this point you are done. You can
checkout master and pull as described in step 1 and your changes should be
there.

## Important points

The important things to remember from this document are

1. You only need to clone and fork once per repository.

2. Always clone from the main repository and add your fork as a remote.

3. Never commit to master. Create a branch and commit to it.

4. Be descriptive in your branch names, commit messages, and pull request
   title and descriptions.

5. Once you have a pull request for a branch, you can push additional changes
   to the same branch and they will be added to the pull request
   automatically. You should never create a new pull request for the same
   branch.

6. Comment on the pull request when you want people to know that you have
   pushed new changes. Although GitHub does notify people of commit pushes,
   people are more likely notice your changes if you leave a comment.
