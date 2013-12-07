# -*- coding: utf-8 -*-
import sys
import traceback
import re
import json
import os
import threading
import xmlrpclib
import markdown2
import sublime, sublime_plugin


u'''文件头样例
<!--iblog
{
    "title":"博客标题写在这里",
    "categories":"博客分类",
    "tags":"标签",
    "publish":"false",
    "blog_id":"3452965"
}
-->
'''
HEADER_TEMPLATE = "<!--iblog\n" + "{\n" + "    \"title\":\"%s\",\n" + "    \"categories\":\"%s\",\n" + "    \"tags\":\"%s\",\n" + "    \"publish\":\"%s\",\n" + "    \"blog_id\":\"%s\"\n" + "}\n" + "-->\n"
HEADER_PATTERN = r'<!--iblog((.|\n)*?)-->'
blog_settings = {}

F_MD = 0
F_PLAIN = 1

class PublishCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.is_dirty():
            sublime.error_message(u'【错误】请先保存在发布！')
            return
        self.header_region = _get_header_region(self.view)
        if not self.header_region:
            sublime.error_message(u'【错误】请填写头部的博客信息！可按<Shift+F8>插入博客信息模板')
            return
        # status: 0-没有执行，1-正在执行，2-执行成功并停止，3-执行失败停止
        self.status = 0 
        self.file_name = self.view.file_name()
        header_str = self.view.substr(self.header_region)
        self.blog_info = _parse_blog_info(header_str)
        # self.action: 1--新建，2--更新
        if not self.blog_info['blog_id']:
            self.action = 1 
        else:
            self.action = 2

        global blog_settings
        if not blog_settings:
            settings = _load_setting()
            blog_settings = {
                'login_name': settings.get('login_name'),
                'login_password': settings.get('login_password'),
                'xml_rpc_url': settings.get('xml_rpc_url'),
            }
        
        file_type = check_file_type(self.file_name)
        content = ''
        if file_type == F_MD:
            region = sublime.Region(0, len(self.view))
            content = self._markdown2html(self.view.substr(region))
        else:
            body_region = sublime.Region(self.header_region.end(), len(self.view))
            content = header_str + _plain2html(self.view.substr(body_region))
        
        self.post = { 'title': self.blog_info['title'],
                'description': content,
                'link': '',
                'author': blog_settings['login_name'],
                'categories': self.blog_info['categories'],
                'mt_keywords': ''
            }
        content = None
        self.server = xmlrpclib.ServerProxy(blog_settings['xml_rpc_url'], allow_none=True)
        self._pulish_async()

    def _pulish_async(self):
        self.status = 1
        if self.action == 1:
            t = threading.Thread(target=self._new_post)
            t.start()
        else:
            t = threading.Thread(target=self._edit_post)
            t.start()
        _show_busy_bar(lambda: self.status != 1, 
            busy_msg=u'正在发布博客', 
            complete_msg='')

    def _new_post(self):
        global blog_settings
        try:
            self.blog_info['blog_id'] = self.server.metaWeblog.newPost("", 
                blog_settings['login_name'], 
                blog_settings['login_password'],
                self.post, 
                self.blog_info['publish']=='true')
        except Exception as e:
            self.status = 3
            _traceback()
            sublime.set_timeout(lambda: sublime.error_message(u'【错误】发布失败！'), 100)
            return

        self.status = 2
        self._update_blog_info()
        sublime.set_timeout(lambda: sublime.message_dialog(u'发布成功！'), 100) # 设置100ms是等待忙时指示条结束
    
    def _edit_post(self):
        global blog_settings
        try:
            self.server.metaWeblog.editPost(self.blog_info['blog_id'], 
                blog_settings['login_name'], 
                blog_settings['login_password'],
                self.post, 
                self.blog_info['publish']=='true')
        except Exception as e:
            self.status = 3
            _traceback()
            sublime.set_timeout(lambda: sublime.error_message(u'【错误】发布失败！'), 10)
            return

        self.status = 2
        sublime.set_timeout(lambda: sublime.message_dialog(u'更新成功！'), 10)

    def _markdown2html(self, content):
        # extras = []
        # try:
        #     import pygments
        #     extras.append('fenced-code-blocks')
        # except ImportError:
        #     _traceback()
        try:
            # markdown2.markdown(content)返回的是markdown2.UnicodeWithAttrs类型，
            # 不被xmlrpclib支持，所以要转换成unicode
            return unicode(markdown2.markdown(content, extras=extras))
        except markdown2.MarkdownError as e:
            _traceback()
            return ''

    def _update_blog_info(self):
        sublime.set_timeout(lambda: self._do_update_blog_info(), 0)

    def _do_update_blog_info(self):
        new_header = HEADER_TEMPLATE % (self.blog_info['title'],
            self.blog_info['categories'],
            self.blog_info['tags'],
            self.blog_info['publish'],
            self.blog_info['blog_id'])
        edit = self.view.begin_edit()
        self.view.replace(edit, self.header_region, new_header)
        self.view.end_edit(edit)         


class InsertHeaderCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        title = ''
        full_name = self.view.file_name()
        if full_name:
            title = os.path.basename(os.path.splitext(full_name)[0])
        header_str = HEADER_TEMPLATE % (title,'','','false','')
        self.view.insert(edit, 0, header_str)


def _parse_blog_info(header_str):
    u'''将文件头字符串解析成blog_info对象'''
    m = re.match(HEADER_PATTERN, header_str)
    if m:
        tmp = json.loads(m.group(1))
        keys = tmp.keys()
        keys.sort()
        if cmp(keys, ['blog_id', 'categories', 'publish', 'tags', 'title']):
            sublime.error_message(u'【错误】博客信息不正确，请按<Shift-F8>重新插入模板并正确填写')
            return None
        blog_info = {}
        for k in keys:
            if k == 'categories':
                blog_info[k] = tmp[k].split(',')
                continue
            blog_info[k] = tmp[k]
        return blog_info
    else:
        return None

def _get_header_region(view):
    header_region = view.find(HEADER_PATTERN, 0)
    if header_region and header_region.begin() == 0:
        return header_region
    # if header_region: #TODO 调试代码，正式环境改用上面的代码
    #     return header_region
    return None

def _load_setting():
    return sublime.load_settings('iblog.blog-settings')

def _show_busy_bar(complete, pos=0, dir=1, busy_msg=u'busy now', complete_msg=u'complete!'):
    '''显示忙时指示条

    complete是无参函数，用来判断是否是忙时。返回False表示是忙时，在状态拦显示一个忙时指示条'''
    if complete():
        sublime.status_message(complete_msg)
        return
    before = pos % 8
    after = 7 - before
    if not after:
        dir = -1
    if not before:
        dir = 1
    pos += dir
    sublime.status_message('%s [%s=%s]' % (busy_msg, ' ' * before, ' ' * after))
    sublime.set_timeout(lambda: _show_busy_bar(complete, pos, dir, busy_msg, complete_msg), 100) 

def check_file_type(file_name):
    if file_name.endswith('.md'):
        return F_MD
    return F_PLAIN

def _plain2html(text):
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
        " ": "&nbsp;"
    }
    escaped = "".join(html_escape_table.get(c,c) for c in text.strip() )
    text = None

    import cStringIO
    if isinstance(escaped, unicode):
        escaped = escaped.encode('utf-8')
    output = cStringIO.StringIO(escaped) #cStringIO不支持unicode
    lines = output.readlines()
    output.close()
    html_output = cStringIO.StringIO()
    html_output.writelines('{0}<br />'.format(x.strip()) for x in lines)
    html = html_output.getvalue()
    html_output.close()
    return unicode(html, 'utf-8')

    
def _traceback():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback.print_exception(exc_type, exc_value, exc_traceback)
