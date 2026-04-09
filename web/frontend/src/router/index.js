import { createRouter, createWebHistory } from 'vue-router'
import ChatView from '../views/ChatView.vue'
import PlanView from '../views/PlanView.vue'
import SpecView from '../views/SpecView.vue'

const routes = [
  {
    path: '/',
    name: 'Chat',
    component: ChatView,
  },
  {
    path: '/chat/:conversationId',
    name: 'ChatWithId',
    component: ChatView,
  },
  {
    path: '/plan',
    name: 'Plan',
    component: PlanView,
  },
  {
    path: '/plan/:planId',
    name: 'PlanWithId',
    component: PlanView,
  },
  {
    path: '/spec',
    name: 'Spec',
    component: SpecView,
  },
  {
    path: '/spec/:featureName',
    name: 'SpecWithId',
    component: SpecView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
