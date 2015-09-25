import io.atomix.catalog.server.StateMachine;
import io.atomix.catalog.server.StateMachineExecutor;

public class MyStateMachine extends StateMachine{
	public void printHello(){
		System.out.println("Hello World!");
	}

	@Override
	protected void configure(StateMachineExecutor arg0) {
		// TODO Auto-generated method stub
		
	}
}
