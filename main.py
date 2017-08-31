#-*- coding:utf-8 -*- 
import web
from handle import Index,RoleProperty,NewUser,DeleteUser,ResetPassword,ChangeUserRole

urls = (
	'/usermanager\/?','Index',
	'/role\/?','RoleProperty',
	'/new_user\/?','NewUser',
	'/delete_user\/?','DeleteUser',
	'/reset_password\/?','ResetPassword',
	'/change_userrole\/?','ChangeUserRole',
)


class MyApplication(web.application):
	def run(self, port=8080, *middleware):
		func = self.wsgifunc(*middleware)
		return web.httpserver.runsimple(func, ('127.0.0.1', port))

#app = web.application(urls,globals())
if __name__ == '__main__':
	#print sgconfig.get_roles_mappings() 
	app = MyApplication(urls, globals())
	app.run(port=5605)


