<!--iblog
{
    "title":"Sublime Text博客插件 --- iblog",
    "categories":"编码与实践",
    "tags":"Python",
    "publish":"true",
    "blog_id":"3463550"
}
-->

iblog是一款 [sublime](http://www.sublimetext.com/ "一款很酷的快平台免费文本编辑器") 博客插件，目前只支持cnblog。

项目地址：<https://github.com/iskeeter/iblog>

功能介绍
---------

* 新建和更新cnblog的博客
* 支持[markdown](http://wowubuntu.com/markdown/)格式，文件必须以 **.md** 为扩展名，否则作为纯文本处理
* 支持发纯文本博客，可以自由书写HTML代码
* 支持代码语法高亮（仅限markdown格式）


安装和设置
----------

1.  设置你的cnblog

    从[这里](https://github.com/iskeeter/iblog)下载插件，用文本编辑器打开 **iblog/iblog.blog-settings** 文件，内容如下：

    ```
    {
        "login_name": "",
        "login_password": "",
        "xml_rpc_url": ""
    }
    ```

    *   `login_name` 博客登陆名
    *   `login_password` 登陆密码
    *   `xml_rpc_url` 在你的博客管理后台的设置页最下面，你可以找到下面这条信息：
        
        MetaWeblog访问地址: http://www.cnblogs.com/[你的用户名]/services/metaweblog.aspx
    
        这个url地址就是要填写的 xml_rpc_url
    
2.  [可选设置] 要支持语法高亮，系统需要安装Python2.6（sublime2支持的是2.6），然后安装Pygments模块
3.  [可选设置] 将style.css中的样式拷贝到cnblog设置页的`通过CSS代码定制代码页面风格`栏中
4.  将iblog目录整个拷贝到sublime插件目录（Preference->Browser Packages）。
5.  OK，一切就绪


开始写博客
----------

1.  按Shift+F8插入头信息，如下：

    ```
    <!--iblog
    {
        "title":"博客标题写在这里",
        "categories":"博客分类",
        "tags":"标签",
        "publish":"false",
        "blog_id":""
    }
    -->
    ```
    
    * `title` 博客标题，默认为文件名
    * `categories` 博客分类，只能填写你已在cnblog上面创建好的分类，多个分类用英文逗号分开
    * `tags` 博客标签
    * `publish` 是否公开（发布）
    * `blog_id` 不需要填写，发布成功后程序自动将刚发布的博客的ID回填在这里，用来判断是否是更新博客

    **不用担心头信息会出现在你的博客里，它会自动被浏览器忽略**

2.  博客写好后按Shift+F9提交  


给cnblog添加markdown样式
------------------------

默认的样式太单调了，你可以找一套漂亮的样式，然后在博客园后天设置你的博客样式。

在博客园后台的``设置``页，找到``首页HTML``栏，填入下面一段代码然后保存。

    <!-- Markdown -->
    <link rel="stylesheet" href="http://files.cnblogs.com/Zjmainstay/Markdown.prettify.css" type="text/css" />
    <style type="text/css">
        pre {border:none}
    </style>
    <!-- Markdown End -->

语法高亮
----------

Sublime插件依赖Python环境，要使本插件支持语法高亮，需要安装 [Pygments](http://pygments.org/ "Python语法高亮模块") 模块。

安装时需要注意的是，Sublime集成的是Python2.6，所以Pygments模块应该安装在Python2.6的模块路径里。

如果是使用easy_install来安装，请使用下面的命令：

    $ easy_install-2.6 pygments

安装好模块后，使用下面的语法来指定语法高亮：

    ```python
    # 代码写在这里
    ```

语法高亮的例子：<http://www.cnblogs.com/skeeter/p/3463551.html>


Enjoy it!
----------












