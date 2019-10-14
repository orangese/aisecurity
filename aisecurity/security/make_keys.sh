#!/usr/bin/env bash

# "aisecurity.security.make_keys"
# Program to create key directory and files
# args: key_dir (directory at which to create keys-- $HOME implied)
#       path_to_json (path to json key list file-- $HOME implied)

key_dir="$1"
path_to_json="$2"

if [ ! -d "$key_dir" ] ; then
  # default locations
  key_dir="$HOME/keys"
  path_to_json="$HOME/keys/key_files.json"
fi

function mk_key_files {
  # Makes key files
  # args: key_loc (key directory)

  key_loc=$1

  if [ ! -d "$key_loc/name_keys.txt" ] ; then
    touch name_keys.txt
    echo "name_keys.txt created in $key_loc"
  else
    echo "name_keys.txt already exists in $key_loc"
  fi

  if [ ! -d "$key_loc/embedding_keys.txt" ] ; then
    touch embedding_keys.txt
    echo "embedding_keys.txt created in $key_loc"
  else
    echo "embedding_keys.txt already exists in $key_loc"
  fi

}

function mk_keys {
  # Makes key files and directory
  # args: dir (directory at which to create keys)

  dir=$key_dir

  if [ ! -d "$dir" ] ; then
    echo "Creating keys directory at $dir"
    mkdir "$dir"
  else
    echo "Keys directory already exists at $dir"
  fi

  cd "$dir" || echo "Something went wrong: $dir cannot be accessed"

  mk_key_files "$dir"
}

function update_json {
  # Updates json key file
  # args: json_path (path to json key file)

  json_path=$path_to_json

  if [ ! -d "$json_path" ] ; then
    echo "Creating json key file at $json_path"
    touch "$json_path"
  fi

  printf '{\n    "names": "%sname_keys.txt",\n    "embeddings": "%sembedding_keys.txt"\n}\n' "$key_dir" "$key_dir" \
  > "$json_path"
}

# make dirs and files
mk_keys "$key_dir"

# update json key file
update_json "$path_to_json"