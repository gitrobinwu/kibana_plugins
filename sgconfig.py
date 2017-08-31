#-*- coding:utf-8 -*-
import re 
import os 

# 用户路径
users_path = '/opt/elk-demo/elasticsearch/plugins/search-guard-2/sgconfig'
hash_path = '/opt/elk-demo/elasticsearch/plugins/search-guard-2/tools'
# 当定义新角色时，需手动添加
role_list  = ['sg_logstash','sg_kibana4_server','sg_kibana4','sg_all_access','sg_kibana4_testindex']

# 获取用户列表
def get_userlist():
	with open(users_path+'/'+'sg_internal_users.yml','r') as f:
		content = f.read() 
		pattern = re.compile(r'username:\s+(\S+)\s+hash',re.S)	
		userlist = re.findall(pattern,content) 
		return userlist 

# form 用户名 密码 角色
# 新建用户
def new_user(username,password,sg_role=None):
	#如果用户已经存在，则返回-1
	if username in get_userlist(): return -1,"用户已经存在"

	# 新建一个用户
	with open(users_path+'/'+'sg_internal_users.yml','a') as f:
		hashpwd = os.popen(hash_path+'/'+'hash.sh'+' '+'-p {pwd}'.format(pwd=password)).read().strip()
		str = '''\n{0}:\n\
  username: {0}\n\
  hash: {1}\n\
  #password is: {2}\
'''.format(username,hashpwd,password)
		f.write(str)

	# 如果选择角色为None,返回-2 
	if sg_role is None: return -2,"选择角色为None"
	sg_list = role_list
	# 如果所选角色不在所给角色列表，返回-3 
	if sg_role not in sg_list: return -3,"所选角色不在所给角色列表"

	# 给用户分配角色
	with open(users_path+'/'+'sg_roles_mapping.yml','r') as f:
		content = f.read() 
		pattern = re.compile(r"{0}:.*?users:(.*?)".format(sg_role),re.S)
		role_str = '''{0}:\n\
  users:\n\
    - {1}\
'''.format(sg_role,username) 
		
		# 如果新建用户已经分配给了所选角色，则返回-4 
		if username in get_role_users(sg_role): return -4,'新建用户已经分配给了所选角色'
		with open(users_path+'/'+'sg_roles_mapping.yml','w') as f:
			f.write(re.sub(pattern,role_str,content))
		return 0,"新建用户成功"

# 删除用户	
def delete_user(username):	
	# 如果用户不存在，则返回-1 
	if username not in get_userlist(): return -1,"删除用户不存在"
	# 删除用户							   
	with open(users_path+'/'+'sg_internal_users.yml','r') as f:
		content = f.read()
		pattern = re.compile(r'{0}:\s+username:\s+{0}\s+hash:\s+\S+\s+#password\s+is:\s+\S+'.format(username),re.S)
		with open(users_path+'/'+'sg_internal_users.yml','w') as f:
			f.write(re.sub(pattern,"",content))

	# 删除用户对应的角色
	with open(users_path+'/'+'sg_roles_mapping.yml','r') as f:
		content = f.read()
		pattern = re.compile(r"\s+-\s+{0}".format(username),re.S)
		with open(users_path+'/'+'sg_roles_mapping.yml','w') as f:
			f.write(re.sub(pattern,"",content))
	return 0,"删除用户成功"

# 获取用户的密码	
def get_userpwd(username):
	if username not in get_userlist(): return -1,"用户不存在"
	with open(users_path+'/'+'sg_internal_users.yml','r') as f:
		content = f.read()
		pattern = re.compile(r'{0}:\s+username:\s+{0}\s+hash:\s+\S+\s+#password\s+is:\s+(\S+)'.format(username),re.S)	 
		pwd = re.findall(pattern,content)
		return pwd 

# 更改用户密码	
def reset_password(username,new_password):
	if username not in get_userlist(): return -1,"用户不存在"
	# 重置用户密码
	with open(users_path+'/'+'sg_internal_users.yml','r') as f:
		content = f.read()
		pattern = re.compile(r"{0}:\s+username:\s+{0}\s+hash:\s+\S+\s+#password\s+is:\s+\S+".format(username),re.S)
		with open(users_path+'/'+'sg_internal_users.yml','w') as f:
			hashpwd = os.popen(hash_path+'/'+'hash.sh'+' '+'-p {pwd}'.format(pwd=new_password)).read().strip()
			str = '''{0}:\n\
  username: {0}\n\
  hash: {1}\n\
  #password is: {2}\
'''.format(username,hashpwd,new_password)
			f.write(re.sub(pattern,str,content))
	return 0,"更改用户密码成功"

# 更改用户角色
def change_userrole(username,sg_role):
	if username not in get_userlist(): return -1,"用户不存在"
	# 先删除用户原先角色
	with open(users_path+'/'+'sg_roles_mapping.yml','r') as f:
		content = f.read()
		pattern = re.compile(r"\s+-\s+{0}".format(username),re.S)
		with open(users_path+'/'+'sg_roles_mapping.yml','w') as f:
			f.write(re.sub(pattern,"",content))

	# 如果选择角色为None,返回-2 
	if sg_role is None: return -2,"选择角色为None"
	sg_list = role_list
	# 如果所选角色不在所给角色列表，返回-3 
	if sg_role not in sg_list: return -3,"所选角色不在所给角色列表"

	#重置用户角色		
	with open(users_path+'/'+'sg_roles_mapping.yml','r') as f:
		content = f.read() 
		pattern = re.compile(r"{0}:.*?users:(.*?)".format(sg_role),re.S)
		role_str = '''{0}:\n\
  users:\n\
    - {1}\
'''.format(sg_role,username) 
		
		# 如果新建用户已经分配给了所选角色，则返回-4 
		if username in get_role_users(sg_role): return -4,'选择的用户已经分配给了所选角色'
		with open(users_path+'/'+'sg_roles_mapping.yml','w') as f:
			f.write(re.sub(pattern,role_str,content))
	return 0,"更改用户角色成功"									   

# 显示角色属性
def display_sg_role(sg_role):
	sg_list = role_list
	if sg_role not in sg_list: return -1,u"当前角色不在可选用角色列表"
	with open(users_path+'/'+'sg_roles.yml','r') as f:
		content = f.read()
		pattern = re.compile(r"({0}:.*?)sg_".format(sg_role),re.S)
		role_property = re.findall(pattern,content) 
		return role_property
	
# 获取角色对应的所有用户
def get_role_users(sg_role):
	with open(users_path+'/'+'sg_roles_mapping.yml','r') as f:
		content = f.read() 
		role_users = []
		pattern = re.compile(r"{0}:.*?users:(.*?)sg_".format(sg_role),re.S)
		for user in re.findall(pattern,content)[0].strip().split('\n'):
			if re.sub(' ','',re.sub('-','',user)) not in role_users:
				role_users.append(re.sub(' ','',re.sub('-','',user)))
		return role_users 

# 获取所有用户角色映射	
def get_roles_mappings():
	with open(users_path+'/'+'sg_roles_mapping.yml','r') as f:
		content = f.read()
		sg_list = role_list
		dict = {}
		roles_user = []
		for sg in sg_list:
			pattern = re.compile(r"({0}):.*?users:(.*?)sg_".format(sg),re.S)
			role_mappings = re.findall(pattern,content)
			for mapping in role_mappings:
				tmp = {}
				tmp['role'] = mapping[0]
				user_lists = mapping[1].strip().split('\n')
				users = []
				for user in user_lists:
					if re.sub(' ','',re.sub('-','',user)) not in users:
						users.append(re.sub(' ','',re.sub('-','',user)))
				tmp['users'] = users  		
				roles_user.append(tmp)
		dict['mapping'] = roles_user  
		return dict 

# 使配置生效		
def run_sgconfig():
	rst = os.popen('sadmin.sh')
	content = rst.read()
	pattern = re.compile(r"Done\s+with\s+success")
	result = re.findall(pattern,content)
	if len(result) != 0:
		return True 
	else: 
		return False 

if __name__ == '__main__':
	print get_userpwd('wuyongwei')
	pass

