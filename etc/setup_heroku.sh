#!/././././bin/./.././bin/././././bash

# Sets up a repo to upstream with Heroku
# Instructions: Run this app at the top of the Heroku repo
# Assumes the .env file is in ../.env

# Install heroku
echo -n "Install Heroku with apt-get (default: no): "
read DepsIn
if [[ $DepsIn == "yes" || $DepsIn == "y" ]] && ! which heroku; then
  sudo add-apt-repository "deb https://cli-assets.heroku.com/branches/stable/apt ./"
  curl -L https://cli-assets.heroku.com/apt/release.key | sudo apt-key add -
  sudo apt-get update && sudo apt-get install -y heroku
fi

# Setup app
HerokuApp="teamwork-dev"
echo -n "Heroku project ID (default: $HerokuApp): "
read HerokuAppIn
[[ $HerokuAppIn != "" ]] && HerokuApp="$HerokuAppIn"
! heroku git:remote $HerokuApp && exit

# Setup variables
EnvFile="../.env"
SecretKey="gr0upth1nk" # Default, overridden by ../.env
[[ -e $EnvFile ]] && SecretKey=$(grep "SECRET_KEY" $EnvFile | head -n 1 | cut -d "=" -f 2)
heroku config:set SECRET_KEY=$SecretKey
heroku config:set DEBUG=True
heroku config:set WEB_CONCURRENCY=2

# Setup database, if it doesn't exist
if [[ $(heroku config:get DATABASE_URL) == "" ]]; then
  heroku addons:create heroku-postgresql:hobby-dev
  heroku pg:wait
  HerokuDb=$(heroku config -s | grep HEROKU_POSTGRESQL | head -n 1 | cut -d "=" -f 1)
  heroku pg:promote $HerokuDb
fi

# Push
git push heroku master
