<%inherit file="/base.mako"/>

<div class="container">

    <h2>Login.</h2>

    <form action="/account/login" method="post">
        <input type="text" name="email" />
        <input type="password" name="password" />
        <input type="hidden" name="method" value="account.login" />
        <input type="submit" />
    </form>

</div>
