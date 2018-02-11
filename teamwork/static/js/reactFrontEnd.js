import React, { Component } from 'react';

import ReactDOM from 'react-dom';



class App extends React.Component {
render() {
    return (
    <div style>
        <h1>Helle Django + React = Awesomeness </h1>
    </div>);
}
}


ReactDOM.render(<App />, document.getElementById('react-app'));
