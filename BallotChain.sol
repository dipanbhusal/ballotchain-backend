pragma solidity ^0.8.7;

contract BallotChain{

    constructor() {
        electionAdmin = msg.sender;
        // electionState = ElectionState.Started;
        // totalVoters=0;
        // totalCandidates=0;
        // elections[_electionAddress].vo=0;

    }

    address public electionAdmin;
    uint256 public totalVoters;
    uint256 public totalCandidates;
    uint256 public countVoteCasted;

    struct Voter{
        address voterAddress;
        bool hasVoted;
        bool isVoter;
        address electionAddress;
    }

    struct Candidate{
        address candidateAddress;
        uint256 totalVotes;
        bool isCandidate;
        address electionAddress;
    }

    struct Result{
        address voterAddress;
        address candidateAddress;
        address electionAddress;

    }

    struct Election{
        address electionAddress;
        uint256 votersCount;
        uint256 candidatesCount;
        uint256 totalCastedVotes;
        ElectionState state;
        bool isActive;
    }

    
    // struct Result{
    // VotingData data;
    // }
    
    enum ElectionState { Started, Voting, Ended } 
    ElectionState public electionState;


    mapping(address=>Voter) public voters; //Creates key-value pairs
    mapping(address=>Candidate) public candidates;
    mapping(address=>Election) public elections;
    Voter[] public votersArray;
    Candidate[] public candidatesArray;
    Result[] electionResultArray;
    
    Election[] public electionArray;
    //Modifiers
    modifier adminOnly(){
        require(msg.sender == electionAdmin, "Only election admin has access.");
        _;
    }

    // modifier inState( ElectionState _state){
    //     require(elections[_electionAddress].state == _state, "In Election Phase");
    //     _;
    // }

    modifier notVoted(){
        require(voters[msg.sender].hasVoted == false, "Current user has already voted.");
        _;
    }

    modifier isVoter(){
        require(voters[msg.sender].isVoter, "User is not voter");
        _;
    }


    event voterAdded(address _voter);
    event candidateAdded(address _candidate);
    event electionStarted();
    event castDone(address _voter);
    event electionEnded();

    function addVoter(address _voterAddress, address _electionAddress) public  adminOnly returns (address){
        require(!voters[_voterAddress].isVoter, "Voter is already registerd in system");
        require(elections[_electionAddress].state == ElectionState.Started, "In Election Preparation Phase");

        voters[_voterAddress] = Voter({
            voterAddress: _voterAddress,
            hasVoted: false,
            isVoter: true,
            electionAddress : _electionAddress
        });
        elections[_electionAddress].votersCount++;
        emit voterAdded(_voterAddress);
        votersArray.push(voters[_voterAddress]);
        return voters[_voterAddress].voterAddress;
    }

    function removeVoter(address _voterAddress) public adminOnly returns(bool){
        require(voters[_voterAddress].isVoter, "Voter with address is not in the system");
        delete voters[_voterAddress];
        if (candidates[_voterAddress].isCandidate){
            delete candidates[_voterAddress];
        }
        return true;
    }

    function addCandidate(address _candidateAddress, address _electionAddress) public adminOnly returns(address){
        require(!candidates[_candidateAddress].isCandidate, "Candidate is already registered in system");
        require(elections[_electionAddress].state == ElectionState.Started, "In Election Preparation Phase");

        candidates[_candidateAddress] = Candidate({
            candidateAddress: _candidateAddress,
            isCandidate: true,
            totalVotes: 0,
            electionAddress:  _electionAddress
        });
        elections[_electionAddress].candidatesCount++;
        emit candidateAdded(candidates[_candidateAddress].candidateAddress);
        candidatesArray.push(candidates[_candidateAddress]);
        return candidates[_candidateAddress].candidateAddress;
    }

    function addElection(address _electionAddress) public adminOnly returns(address){
        require(!elections[_electionAddress].isActive, "Election already exists");
        elections[_electionAddress] = Election({
            electionAddress: _electionAddress,
            votersCount: 0,
            candidatesCount: 0,
            totalCastedVotes: 0,
            state: ElectionState.Started,
            isActive: true
        });
        return elections[_electionAddress].electionAddress;

    }

    function startElection(address _electionAddress) public  adminOnly {
        require(elections[_electionAddress].state==ElectionState.Started, "Election is already started");
        elections[_electionAddress].state = ElectionState.Voting;
        elections[_electionAddress].isActive = true;
        emit electionStarted();
    }
    
    function castVote(address _candidateAddress, address _electionAddress) public notVoted isVoter {
        require(candidates[_candidateAddress].isCandidate, "User can vote to candidate only");
        require(elections[_electionAddress].state == ElectionState.Voting, "Election is not started");
        voters[msg.sender].hasVoted = true;
        candidates[_candidateAddress].totalVotes++;
        elections[_electionAddress].totalCastedVotes++;
        
        Result memory res = Result(msg.sender, _candidateAddress, _electionAddress);
        electionResultArray.push(res);

    }


    function endElection(address _electionAddress) public adminOnly returns(uint256){
        require(elections[_electionAddress].state==ElectionState.Voting, "Election is not started");
        elections[_electionAddress].state = ElectionState.Started;
        elections[_electionAddress].isActive = false;
        emit electionEnded();
        return elections[_electionAddress].totalCastedVotes;
    }

    Result[] tempArray;

    function electionResult(address _electionAddress) public  returns(Result[] memory){
        // return electionResultArray;
        delete tempArray;
        for(uint256 i=0; i<electionResultArray.length; i++){
            if(electionResultArray[i].electionAddress == _electionAddress){
                tempArray.push(electionResultArray[i]);
            }
        }
        return tempArray;

    } 
}