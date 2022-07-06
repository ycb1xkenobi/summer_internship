import React from "react";
import Header from "./components/Header"; 
import Users from "./components/Users"; 
import AddUser from "./components/AddUser";


class App extends React.Component {
  

  componentDidUpdate(prevProp){
    if(this.state.text !== "Here")
      console.log("Some")
  }


  render(){
    return(
    <div className="name"> 
     <Header title = "Регистрация пользователя"/>
     <aside>
        <AddUser/>
     </aside>
    </div>
    )
  }

}

export default App