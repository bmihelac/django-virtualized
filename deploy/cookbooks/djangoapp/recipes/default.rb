execute "Update apt repos" do
    command "apt-get update"
end

include_recipe 'build-essential'
include_recipe 'nginx'
include_recipe 'python'
#include_recipe 'runit'
include_recipe 'git'

#execute "restart postgres" do
    #command "sudo /etc/init.d/postgresql-8.4 restart"
#end

#execute "create-database" do
    #command "createdb -U postgres -O postgres #{node[:dbname]}"
#end

