````
sudo npm update npm -g
sudo npm install -g yarn

YARN_CMD="/usr/local/lib/node_modules/yarn/bin/yarn"

mkdir ckeditor5
cd ckeditor5
git clone https://github.com/ckeditor/ckeditor5 .

# install yarn
$YARN_CMD install --ignore-engines

# edit packages/ckeditor5-build-classic/src/ckeditor.js
# add/change plugins and default configuration

pushd packages/ckeditor5-build-classic/
$YARN_CMD config set ignore-engines true

# edit packages/ckeditor5-build-classic/ckeditor.js - put modules
# then
/usr/local/lib/node_modules/yarn/bin/yarn run build

````


