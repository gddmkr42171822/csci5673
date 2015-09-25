import java.util.Arrays;
import java.util.List;

import io.atomix.catalog.client.RaftClient;
import io.atomix.catalyst.transport.Address;
import io.atomix.catalyst.transport.NettyTransport;

public class JavaRaftClient1 {

	public static void main(String[] args) {
		List<Address> members = Arrays.asList(
				  new Address("127.0.0.1", 5555),
				  new Address("127.0.0.1", 6666)
				);
		RaftClient client = RaftClient.builder(members)
				  .withTransport(new NettyTransport())
				  .build();
		client.open().thenRun(() -> System.out.println("Client 1 successfully connected to the cluster!"));		
		//client.session().onEvent(message -> System.out.println("Received " + message));

	}

}
