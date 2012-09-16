<%inherit file="../base.mako"/>

<div class="container">

    <h2>Create account.</h2>

    <form action="/account/create" method="post">
        <input type="text" name="email" />
        <input type="password" name="password" />
        <input type="password" name="password_confirm" />
        <input type="hidden" name="method" value="account.create" />
        <input type="submit" />
    </form>

</div>
