<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />

    <title>foo</title>

    ${h.stylesheet_link(request, 'foo.web:static/css/base.css')}

    <%block name="extra_head">
    </%block>
</head>

<body>

<%block name="header">
<header>
    <div class="container">
        <h1 class="logo"><a href="/">foo</a></h1>
    </div>
</header>
</%block>

<%
    flash = request.session.pop_flash()
%>
% if flash:
<div class="container">
    <ul id="flash-messages">
    % for message in flash:
        <li class="info">${message}</li>
    % endfor
    </ul>
</div>
% endif

<div class="content">
${next.body()}
</div>

<footer>
    <div class="container">
        <p>
            &hearts;
        </p>
    </div>
</footer>

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9/jquery.min.js"></script>

<%block name="tail" />

</body>

</html>
