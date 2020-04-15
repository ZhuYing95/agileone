#!/usr/bin/env python
# -*- coding: utf-8 -*-

import HTMLTestRunner
import requests
import os
import time
import unittest


# 封装requests库的get和post请求方法为一个自定义类
class Connection:
    def __init__(self, host, port=80):
        self.base_url = 'http://%s:%d' % (host, port)
        self.session = requests.session()

    def get(self, url, params=None, headers=None):
        if headers is None:
            headers = {}
        response = self.session.get(
            self.base_url + url, params=params, headers=headers)
        return response

    def post(self, url, data, headers=None):
        if headers is None:
            headers = {}
        response = self.session.post(
            self.base_url + url, data=data, headers=headers)
        return response

    # 清理资源，关闭会话
    def close(self):
        self.session.close()


# 构造一个针对Agileone的测试类
class Agileone(unittest.TestCase):
    """Agileone接口测试示例"""

    con = None

    @classmethod
    def setUpClass(cls):
        cls.con = Connection('192.168.1.105')

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_01_access_agileone(self):
        """打开Agileone网站主页"""
        resp = self.con.get('/agileone/')
        self.assertEqual(200, resp.status_code)
        self.assertEqual('OK', resp.reason)
        self.assertIn('AgileOne - Welcome to Login',
                      resp.content.decode('utf-8'))

    def test_02_login_agileone(self):
        """登录Agileone网站"""
        test_data = [{'username': '', 'password': '', 'savelogin': False},
                     {'username': 'a', 'password': '', 'savelogin': False},
                     {'username': 'admin', 'password': '1a',
                      'savelogin': False},
                     {'username': 'ab', 'password': 'admin',
                      'savelogin': False},
                     {'username': 'admin', 'password': 'admin',
                      'savelogin': False}]
        for params in test_data:
            resp = self.con.post('/agileone/index.php/common/login', params)
            self.assertEqual(200, resp.status_code)
            self.assertEqual('OK', resp.reason)
            if params['username'] == 'admin' and params['password'] == 'admin':
                self.assertEqual('successful', resp.text)
            elif params['username'] == 'admin' and\
                    params['password'] != 'admin':
                self.assertEqual('password_invalid', resp.text)
            else:
                self.assertEqual('user_invalid', resp.text)

    def test_03_notice_add(self):
        """发布公告"""
        # 执行此方法会发现没有公告标题也会成功添加公告的错误
        test_data = ['test', '', '0a!kl']
        date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        # 方法一
        errors = []
        for title in test_data:
            params = {'headline': title, 'expireddate': date, 'scope': 1}
            resp = self.con.post('/agileone/index.php/notice/add', params)
            try:
                self.assertEqual(200, resp.status_code)
                self.assertEqual('OK', resp.reason)
                if len(title):
                    self.assertGreater(int(resp.text), 0)
                else:
                    # 此处传入的headline为空字符串，期望返回错误消息，而不是添加公告成功的id
                    self.assertRaises(ValueError, int, resp.text)
            except AssertionError as e:
                errors.append('The server return a response id "%s" when\
                               title is "%s".' % (resp.text, title))
        if len(errors):
            raise AssertionError(*errors)
        # 方法二
        # for title in test_data:
        #     # 注意这个subTest方法仅在python 3环境下才支持。
        #     with self.subTest(title, headline=title):
        #         params = {'headline': title, 'expireddate': date, 'scope': 1}
        #         resp = self.con.post('/agileone/index.php/notice/add', params)
        #         self.assertEqual(200, resp.status_code)
        #         self.assertEqual('OK', resp.reason)
        #         if len(title):
        #             self.assertGreater(int(resp.text), 0)
        #         else:
        #             # 此处传入的headline为空字符串，期望返回错误消息，而不是添加公告成功的id
        #             self.assertRaises(ValueError, int, resp.text)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(Agileone)
    now = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    report_path = os.path.join(os.getcwd(), 'report')
    if not os.path.exists(report_path):
        os.makedirs(report_path)
    report = os.path.join(report_path, 'agileone_test_report_%s.html' % now)
    with open(report, "w", encoding='utf8') as f:
        runner = HTMLTestRunner.HTMLTestRunner(title='agileone',
                                               description='Test Report',
                                               stream=f, verbosity=2)
        runner.run(suite)

