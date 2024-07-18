import { createRouter, createWebHistory } from 'vue-router'
import Login from "../views/Login/index.vue"
import TextEditor from "../views/TextEditor/index.vue"
import UserProfile from "../views/UserProfile/index.vue"

const isLoggedIn = () => {
	return localStorage.getItem('token') && localStorage.getItem('account')
}

const router = createRouter({
	history: createWebHistory(),
	routes: [
		{
			path: '/',
			redirect: (_to) => {
				return isLoggedIn() ? '/editor' : '/login'
			}
		},
		{
			path: '/login',
			component: Login,
		},
		{
			path: '/editor',
			component: TextEditor,
			meta: { isAuth: true },
		},
		{
			path: '/user-profile',
			component: UserProfile,
			meta: { isAuth: true },
		}
	]
})

router.beforeEach((to, from, next) => {
	console.log('beforeEach', to, from)
	if (to.meta.isAuth) { //判断当前路由是否需要进行权限控制
		if (isLoggedIn()) { //权限控制的具体规则
			next() //放行
		} else {
			next("/login")
		}
	} else {
		if (to.path === '/login' && isLoggedIn()) {
			next('/editor')
		} else {
			next() //放行
		}
	}
})
export default router