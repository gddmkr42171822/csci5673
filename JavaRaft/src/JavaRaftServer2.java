import java.util.Arrays;
import java.util.List;

import io.atomix.catalog.server.RaftServer;
import io.atomix.catalog.server.storage.Storage;
import io.atomix.catalyst.transport.Address;
import io.atomix.catalyst.transport.NettyTransport;

public class JavaRaftServer2 {

	public static void main(String[] args) {
		List<Address> members = Arrays.asList(
				new Address("127.0.0.1", 6666)
				);
		RaftServer server = RaftServer.builder(new Address("127.0.0.1", 5555), members)
				.withTransport(new NettyTransport())
				.withStorage(new Storage("logs"))
				.withStateMachine(new MyStateMachine())
				.build();
		server.open().thenRun(() -> System.out.println("Server 2 started successfully!"));
	}
	
}
