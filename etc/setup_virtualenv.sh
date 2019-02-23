#!/././././bin/./.././bin/././././bash

# Sets up a virtual environment in a location of your choosing
# Clones in GroupThink repo
# Copies out sample .env file

# Save current location
Pwd="$(pwd)"

# Install dependencies
echo -n "Install dependencies with apt-get (default: no): "
read DepsIn
if [[ $DepsIn == "yes" || $DepsIn == "y" ]]; then
  Packages="python3 python3-dev python-virtualenv postgresql python-psycopg2 libpq-dev libjpeg8-dev"
  for Package in $Packages; do
    if ! dpkg -s $Package >/dev/null 2>&1; then
      sudo apt-get install -y $Package
    fi
  done
fi

# Create virtual environment
EnvDir="$Pwd/gtdev"
echo -n "Virtual environment dir (default: $EnvDir): "
read EnvDirIn
[[ $EnvDirIn != "" ]] && EnvDir="$EnvDirIn"
[[ ! -e $EnvDir ]] && virtualenv -p python3 $EnvDir
cd $EnvDir

# Clone repo
RepoDir="$EnvDir"
RepoUrl="git@github.com:andgates/teamwork-project.git"
echo -n "Repo url (default: $RepoUrl): "
read RepoUrlIn
[[ $RepoUrlIn != "" ]] && EnvDir="RepoUrlIn"
[[ ! -e $RepoDir ]] && git clone $RepoUrl

# Copy .env file
SampleEnv="$RepoDir/etc/example.env"
EnvFile="$EnvDir/.env"
[[ ! -e $EnvFile ]] && cp $SampleEnv $EnvFile
