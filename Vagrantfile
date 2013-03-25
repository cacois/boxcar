Vagrant::Config.run do |config|
  config.vm.box = "precise64"
  
  config.vm.forward_port 3000, 3000

  config.vm.share_folder "test_app", "/home/vagrant/test_app", "test_app"

  # allow for symlinks in the test_app folder
  config.vm.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/test_app", "1"]
  config.vm.customize ["modifyvm", :id, "--memory", 512]

  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = "cookbooks"
    chef.add_recipe "apache2"
    chef.add_recipe "python"
    chef.add_recipe "django"

  end
end