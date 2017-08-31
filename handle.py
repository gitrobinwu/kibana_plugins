#-*- coding:utf-8 -*- 
from sgconfig import get_roles_mappings,display_sg_role,new_user
from sgconfig import run_sgconfig,get_role_users,delete_user
from sgconfig import users_path,role_list 
from sgconfig import get_userpwd,reset_password,change_userrole
import web 
import re 
import os 

render = web.template.render('templates/',base="layout")

# 主页
class Index(object):
	# 返回角色-用户映射	
	def GET(self):
		return render.index(get_roles_mappings()['mapping'])

#查看角色属性		
class RoleProperty(object):
	def GET(self):
		sg_role = web.input()
		display_role =  display_sg_role(sg_role.sg)[0].strip()
		property = re.sub('-','&nbsp;&nbsp;&nbsp;&nbsp;-',re.sub(r'\n','<br/>',display_role))
		return render.roleproperty(property) 

#新建用户	
class NewUser(object):
	def __init__(self):
		sg_list = role_list
		args = []
		for role in sg_list:
			args.append((role,role))
		self.sg_select = web.form.Dropdown(name='sg_role', args=args, value='sg_kibana4').render() 

	def GET(self):
		return render.newuser(self.sg_select,message="")

	def POST(self):	
		form = web.input(username=None,password=None)
		# 判断输入的合法性
		print form.username,form.password,form.sg_role 
		if not form.username: return render.newuser(self.sg_select,"用户名为空")
		if len(form.username)>18: return render.newuser(self.sg_select,"用户长度最多为18位")
		if len(re.findall(r"[^a-z]",form.username))!=0: return render.newuser(self.sg_select,"用户名只能匹配[a-z]")
		if not form.password: return render.newuser(self.sg_select,"密码为空")
		if len(form.password)>11: return render.newuser(self.sg_select,"密码长度最多为11位")
		if len(re.findall(r"[^0-9a-z]",form.password))!=0: return render.newuser(self.sg_select,"密码不合法，只能匹配[0-9a-z]")
		
		#新建用户
		rst = new_user(form.username,form.password,form.sg_role)
		if rst[0] == 0:
			# 删除多余的空行
			os.popen(r"sed -i '/^\s*$/d' {0}".format(users_path+'/'+'sg_internal_users.yml'))
			# 激活配置
			if run_sgconfig():
				return render.newuser(self.sg_select,rst[1]+"，同时处于激活状态!")
			else:
				return render.newuser(self.sg_select,rst[1]+"但是激活用户失败!")
		else:
			return render.newuser(self.sg_select,rst[1])
				
		raise web.seeother('/')		

#删除用户
class DeleteUser(object):
	def __init__(self):
		sg_list = role_list
		args = []
		for role in sg_list:
			for user in get_role_users(role):
				args.append(user)
		# 不能删除的用户		
		beyond = ["logstash","admin","adm","kibanaserver","kibanaro","test"]
		[args.pop(args.index(x)) for x in beyond if x in args]
		if not args: 
			self.user_select = None  
		else:
			self.user_select = web.form.Dropdown(name='user', args=args, value=args[0]).render()

	def GET(self):
		if not self.user_select:
			msg = "当前没有可删除的用户"
		else:
			msg = ""
		return render.deleteuser(self.user_select,message=msg)
	
	def POST(self):
		form = web.input()
		print form.user

		# 删除用户
		rst = delete_user(form.user)
		if rst[0] == 0:
			# 删除多余的空行
			os.popen(r"sed -i '/^\s*$/d' {0}".format(users_path+'/'+'sg_internal_users.yml'))
			# 激活配置
			if run_sgconfig():
				return render.deleteuser(self.user_select,rst[1]+"，同时处于激活状态!")
			else:	
				return render.deleteuser(self.user_select,rst[1]+",但是激活用户失败!")
		else:
			return render.deleteuser(self.user_select,rst[1])
		raise web.seeother('/')		

#更改用户密码		
class ResetPassword(object):
	def __init__(self):
		sg_list = role_list
		args = []
		for role in sg_list:
			for user in get_role_users(role):
				args.append(user)
		# 不能更改密码的用户		
		beyond = ["logstash","admin","adm","kibanaserver","kibanaro","test"]
		[args.pop(args.index(x)) for x in beyond if x in args]
		if not args: 
			self.reset_users = None  
		else:
			self.reset_users = web.form.Dropdown(name='resetuser', args=args, value=args[0]).render()
		

	def GET(self):
		if not self.reset_users: 
			msg = "当前没有可更改密码的用户"
		else:
			msg = ""
		return render.resetpassword(self.reset_users,message=msg)
	
	def POST(self):
		form = web.input()
		print form.resetuser,form.resetpwd
		#检测输入的合法性
		if not form.resetpwd: return render.resetpassword(self.reset_users,"密码为空")
		if len(form.resetpwd)>11: return render.resetpassword(self.reset_users,"密码长度最多为11位")
		if len(re.findall(r"[^0-9a-z]",form.resetpwd))!=0: return render.resetpassword(self.reset_users,"密码不合法，只能匹配[0-9a-z]")
		if get_userpwd(form.resetuser)[0] == form.resetpwd:
			return render.resetpassword(self.reset_users,"和旧密码一样，请重新输入!")

		#更改密码
		rst = reset_password(form.resetuser,form.resetpwd)
		if rst[0] == 0:
			# 激活配置
			if run_sgconfig():
				return render.resetpassword(self.reset_users,rst[1]+"，同时处于激活状态!")
			else:
				return render.resetpassword(self.reset_users,rst[1]+",但是激活用户失败!")
		else:
			return render.resetpassword(self.reset_users,rst[1])
		
#更改用户角色
class ChangeUserRole(object):
	def __init__(self):
		sg_list = role_list
		args = []
		for role in sg_list:
			for user in get_role_users(role):
				args.append(user)
		# 不能更改密码的用户		
		beyond = ["logstash","admin","adm","kibanaserver","kibanaro","test"]
		[args.pop(args.index(x)) for x in beyond if x in args]
		if not args: 
			self.users_list = None  
		else:
			self.users_list = web.form.Dropdown(name='selectuser', args=args, value=args[0]).render()
		self.roles_list = web.form.Dropdown(name='selectrole', args=sg_list, value='sg_kibana4').render() 

	def GET(self):
		if not self.users_list:
			msg = "当前没有可更改角色的用户"
		else:
			msg = ""
		return render.changeuserrole(self.users_list,self.roles_list,message=msg)
		
	def POST(self):
		form = web.input()
		print form.selectuser,form.selectrole

		#更改用户角色
		rst = change_userrole(form.selectuser,form.selectrole)
		if rst[0] == 0:
			# 激活配置
			if run_sgconfig():
				return render.changeuserrole(self.users_list,self.roles_list,rst[1]+"，同时处于激活状态!")
			else:
				return render.changeuserrole(self.users_list,self.roles_list,rst[1]+",但是激活用户失败!")
		else:
			return render.changeuserrole(self.users_list,self.roles_list,rst[1])

if __name__ == '__main__':
	#print web.form.Dropdown(name='foo', args=[('a', 'aa'), ('b', 'bb'), ('c', 'cc')], value='b').render()
	run_sgconfig() # 激活配置

	
